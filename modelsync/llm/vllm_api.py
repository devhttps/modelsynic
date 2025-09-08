"""
API para vLLM - Servicio de inferencia de modelos de lenguaje
Integrado con ModelSync para versionado de modelos LLM
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import asyncio
import logging
from datetime import datetime
import json
import uuid
from contextlib import asynccontextmanager
import os
from pathlib import Path

# Importar componentes de ModelSync
from modelsync.core.versioning import ModelSyncRepo
from modelsync.storage.model_storage import ModelStorage
from modelsync.collaboration.audit import AuditLog

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelos Pydantic
class GenerationRequest(BaseModel):
    prompt: str = Field(..., description="Texto de entrada para generar")
    max_tokens: int = Field(100, description="Número máximo de tokens a generar")
    temperature: float = Field(0.7, description="Temperatura para la generación (0.0-2.0)")
    top_p: float = Field(0.9, description="Top-p sampling (0.0-1.0)")
    top_k: int = Field(50, description="Top-k sampling")
    stop: Optional[List[str]] = Field(None, description="Secuencias de parada")
    stream: bool = Field(False, description="Si debe generar streaming")
    model_name: Optional[str] = Field(None, description="Nombre del modelo a usar")
    save_to_version_control: bool = Field(True, description="Guardar en ModelSync")

class GenerationResponse(BaseModel):
    id: str
    text: str
    finish_reason: str
    usage: Dict[str, int]
    model: str
    created: str
    model_version_id: Optional[str] = None

class ModelInfo(BaseModel):
    name: str
    size: str
    status: str
    loaded_at: str
    version_control_id: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    models_loaded: int
    uptime: str
    version: str
    modelsync_status: str

# Variables globales para el modelo
vllm_engine = None
loaded_models = {}
start_time = datetime.now()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    global vllm_engine, start_time
    
    # Inicialización
    logger.info("Iniciando vLLM API con integración ModelSync...")
    start_time = datetime.now()
    
    try:
        # Verificar si vLLM está disponible
        try:
            import vllm
            vllm_available = True
        except ImportError:
            vllm_available = False
            logger.warning("vLLM no está instalado. Usando modo simulado.")
        
        if vllm_available:
            # Cargar modelo por defecto
            vllm_engine = vllm.LLM(
                model="meta-llama/Meta-Llama-3-8B-Instruct",
                trust_remote_code=True,
                tensor_parallel_size=1,
                gpu_memory_utilization=0.8
            )
            loaded_models["default"] = {
                "name": "meta-llama/Meta-Llama-3-8B-Instruct",
                "size": "8B",
                "status": "loaded",
                "loaded_at": datetime.now().isoformat(),
                "version_control_id": None
            }
            logger.info("Modelo vLLM cargado exitosamente")
        else:
            # Modo simulado para desarrollo
            loaded_models["default"] = {
                "name": "simulated-model",
                "size": "simulated",
                "status": "simulated",
                "loaded_at": datetime.now().isoformat(),
                "version_control_id": None
            }
            logger.info("Modo simulado activado")
            
    except Exception as e:
        logger.error(f"Error al cargar el modelo: {e}")
        vllm_engine = None
    
    yield
    
    # Limpieza
    logger.info("Cerrando vLLM API...")
    if vllm_engine:
        del vllm_engine

# Crear aplicación FastAPI
app = FastAPI(
    title="ModelSync vLLM API",
    description="API de inferencia para modelos de lenguaje usando vLLM con integración ModelSync",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencias
def get_model_storage() -> ModelStorage:
    return ModelStorage()

def get_audit_log() -> AuditLog:
    return AuditLog()

def get_repo() -> ModelSyncRepo:
    return ModelSyncRepo()

# Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "ModelSync vLLM API - Servicio de inferencia de modelos de lenguaje",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "modelsync_integration": "enabled"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Verificación de salud del servicio"""
    uptime = str(datetime.now() - start_time)
    modelsync_status = "connected" if get_repo().is_initialized() else "not_initialized"
    
    return HealthResponse(
        status="healthy" if vllm_engine or "simulated" in str(loaded_models.get("default", {})),
        models_loaded=len(loaded_models),
        uptime=uptime,
        version="1.0.0",
        modelsync_status=modelsync_status
    )

@app.get("/models", response_model=List[ModelInfo])
async def list_models():
    """Listar modelos cargados"""
    models = []
    for model_id, info in loaded_models.items():
        models.append(ModelInfo(
            name=info["name"],
            size=info["size"],
            status=info["status"],
            loaded_at=info["loaded_at"],
            version_control_id=info.get("version_control_id")
        ))
    return models

@app.post("/generate", response_model=GenerationResponse)
async def generate_text(
    request: GenerationRequest,
    model_storage: ModelStorage = Depends(get_model_storage),
    audit_log: AuditLog = Depends(get_audit_log)
):
    """Generar texto usando el modelo cargado"""
    if not vllm_engine and "simulated" not in str(loaded_models.get("default", {})):
        raise HTTPException(status_code=503, detail="Modelo no cargado")
    
    try:
        # Generar texto
        start_time = datetime.now()
        
        if vllm_engine:
            # Configurar parámetros de generación
            generation_params = {
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "top_p": request.top_p,
                "top_k": request.top_k,
            }
            
            if request.stop:
                generation_params["stop"] = request.stop
            
            # Generar texto
            outputs = vllm_engine.generate([request.prompt], **generation_params)
            output = outputs[0]
            generated_text = output.outputs[0].text
            finish_reason = output.outputs[0].finish_reason
        else:
            # Modo simulado
            generated_text = f"Respuesta simulada para: {request.prompt[:50]}..."
            finish_reason = "stop"
        
        end_time = datetime.now()
        
        # Calcular uso de tokens (aproximado)
        input_tokens = len(request.prompt.split())
        output_tokens = len(generated_text.split())
        
        # Guardar en ModelSync si está habilitado
        model_version_id = None
        if request.save_to_version_control:
            try:
                # Crear metadatos del modelo
                model_metadata = {
                    "prompt": request.prompt,
                    "generated_text": generated_text,
                    "parameters": {
                        "max_tokens": request.max_tokens,
                        "temperature": request.temperature,
                        "top_p": request.top_p,
                        "top_k": request.top_k
                    },
                    "usage": {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "total_tokens": input_tokens + output_tokens
                    },
                    "generation_time": (end_time - start_time).total_seconds()
                }
                
                # Guardar como modelo en ModelSync
                model_info = model_storage.add_model(
                    model_path="generated_text.txt",  # Archivo temporal
                    model_name=f"llm_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    framework="vllm",
                    metrics={"generation_time": (end_time - start_time).total_seconds()},
                    hyperparameters=model_metadata["parameters"],
                    training_info=model_metadata
                )
                model_version_id = model_info["id"]
                
                # Log de auditoría
                audit_log.log_action(
                    action="llm_generation",
                    user="api_user",
                    resource_type="model",
                    resource_id=model_version_id,
                    details={
                        "prompt_length": len(request.prompt),
                        "response_length": len(generated_text),
                        "generation_time": (end_time - start_time).total_seconds()
                    }
                )
                
            except Exception as e:
                logger.warning(f"Error al guardar en ModelSync: {e}")
        
        response = GenerationResponse(
            id=str(uuid.uuid4()),
            text=generated_text,
            finish_reason=finish_reason,
            usage={
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            },
            model=loaded_models.get("default", {}).get("name", "unknown"),
            created=datetime.now().isoformat(),
            model_version_id=model_version_id
        )
        
        logger.info(f"Generación completada en {(end_time - start_time).total_seconds():.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error en generación: {e}")
        raise HTTPException(status_code=500, detail=f"Error en generación: {str(e)}")

@app.post("/generate/batch", response_model=List[GenerationResponse])
async def generate_batch(
    requests: List[GenerationRequest],
    model_storage: ModelStorage = Depends(get_model_storage),
    audit_log: AuditLog = Depends(get_audit_log)
):
    """Generar texto para múltiples prompts en lote"""
    if not vllm_engine and "simulated" not in str(loaded_models.get("default", {})):
        raise HTTPException(status_code=503, detail="Modelo no cargado")
    
    if len(requests) > 10:  # Límite de seguridad
        raise HTTPException(status_code=400, detail="Máximo 10 prompts por lote")
    
    try:
        responses = []
        prompts = [req.prompt for req in requests]
        
        # Usar parámetros del primer request
        first_request = requests[0]
        generation_params = {
            "max_tokens": first_request.max_tokens,
            "temperature": first_request.temperature,
            "top_p": first_request.top_p,
            "top_k": first_request.top_k,
        }
        
        if first_request.stop:
            generation_params["stop"] = first_request.stop
        
        # Generar para todos los prompts
        if vllm_engine:
            outputs = vllm_engine.generate(prompts, **generation_params)
        else:
            # Modo simulado
            outputs = [type('obj', (object,), {'outputs': [type('obj', (object,), {'text': f"Respuesta simulada para: {prompt[:50]}...", 'finish_reason': 'stop'})]}) for prompt in prompts]
        
        for i, output in enumerate(outputs):
            generated_text = output.outputs[0].text
            finish_reason = output.outputs[0].finish_reason
            
            input_tokens = len(requests[i].prompt.split())
            output_tokens = len(generated_text.split())
            
            # Guardar en ModelSync si está habilitado
            model_version_id = None
            if requests[i].save_to_version_control:
                try:
                    model_metadata = {
                        "prompt": requests[i].prompt,
                        "generated_text": generated_text,
                        "parameters": generation_params,
                        "usage": {
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens,
                            "total_tokens": input_tokens + output_tokens
                        }
                    }
                    
                    model_info = model_storage.add_model(
                        model_path="generated_text.txt",
                        model_name=f"llm_batch_generation_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        framework="vllm",
                        metrics={"generation_time": 0.0},
                        hyperparameters=generation_params,
                        training_info=model_metadata
                    )
                    model_version_id = model_info["id"]
                    
                except Exception as e:
                    logger.warning(f"Error al guardar en ModelSync: {e}")
            
            response = GenerationResponse(
                id=str(uuid.uuid4()),
                text=generated_text,
                finish_reason=finish_reason,
                usage={
                    "prompt_tokens": input_tokens,
                    "completion_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                },
                model=loaded_models.get("default", {}).get("name", "unknown"),
                created=datetime.now().isoformat(),
                model_version_id=model_version_id
            )
            responses.append(response)
        
        # Log de auditoría para el lote
        audit_log.log_action(
            action="llm_batch_generation",
            user="api_user",
            resource_type="batch",
            resource_id=str(uuid.uuid4()),
            details={
                "batch_size": len(requests),
                "total_prompts": len(prompts)
            }
        )
        
        return responses
        
    except Exception as e:
        logger.error(f"Error en generación por lotes: {e}")
        raise HTTPException(status_code=500, detail=f"Error en generación por lotes: {str(e)}")

@app.get("/modelsync/status")
async def modelsync_status(repo: ModelSyncRepo = Depends(get_repo)):
    """Estado de la integración con ModelSync"""
    if not repo.is_initialized():
        return {
            "status": "not_initialized",
            "message": "ModelSync repository not initialized",
            "init_endpoint": "/modelsync/init"
        }
    
    status_info = repo.status()
    return {
        "status": "initialized",
        "repository_info": status_info,
        "modelsync_version": "0.1.0"
    }

@app.post("/modelsync/init")
async def init_modelsync(
    user_name: str = "vLLM API User",
    user_email: str = "vllm@modelsync.local",
    repo: ModelSyncRepo = Depends(get_repo)
):
    """Inicializar repositorio ModelSync"""
    try:
        success = repo.init(user_name, user_email)
        if success:
            return {"message": "ModelSync repository initialized successfully", "status": "success"}
        else:
            return {"message": "ModelSync repository already initialized", "status": "info"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics(audit_log: AuditLog = Depends(get_audit_log)):
    """Obtener métricas del servicio"""
    # Obtener métricas de auditoría
    recent_actions = audit_log.get_audit_trail()[:10]
    
    return {
        "models_loaded": len(loaded_models),
        "total_requests": len([a for a in recent_actions if "generation" in a.get("action", "")]),
        "average_response_time": 0.0,  # En una implementación real, calcularías esto
        "memory_usage": "unknown",
        "gpu_usage": "unknown",
        "modelsync_integration": "active",
        "recent_activity": len(recent_actions)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "modelsync.llm.vllm_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
