"""
Cliente para la API de vLLM integrada con ModelSync
"""

import requests
import json
from typing import List, Optional, Dict, Any
from datetime import datetime

class VLLMClient:
    """Cliente para interactuar con la API de vLLM integrada con ModelSync"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Verificar el estado del servicio"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def list_models(self) -> List[Dict[str, Any]]:
        """Listar modelos disponibles"""
        response = self.session.get(f"{self.base_url}/models")
        response.raise_for_status()
        return response.json()
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        stop: Optional[List[str]] = None,
        model_name: Optional[str] = None,
        save_to_version_control: bool = True
    ) -> Dict[str, Any]:
        """Generar texto con integración ModelSync"""
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "stream": False,
            "save_to_version_control": save_to_version_control
        }
        
        if stop:
            payload["stop"] = stop
        if model_name:
            payload["model_name"] = model_name
        
        response = self.session.post(f"{self.base_url}/generate", json=payload)
        response.raise_for_status()
        return response.json()
    
    def generate_batch(
        self,
        prompts: List[str],
        max_tokens: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        stop: Optional[List[str]] = None,
        save_to_version_control: bool = True
    ) -> List[Dict[str, Any]]:
        """Generar texto para múltiples prompts en lote"""
        requests_data = []
        for prompt in prompts:
            request_data = {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "stream": False,
                "save_to_version_control": save_to_version_control
            }
            if stop:
                request_data["stop"] = stop
            requests_data.append(request_data)
        
        response = self.session.post(f"{self.base_url}/generate/batch", json=requests_data)
        response.raise_for_status()
        return response.json()
    
    def get_modelsync_status(self) -> Dict[str, Any]:
        """Obtener estado de la integración ModelSync"""
        response = self.session.get(f"{self.base_url}/modelsync/status")
        response.raise_for_status()
        return response.json()
    
    def init_modelsync(
        self,
        user_name: str = "vLLM API User",
        user_email: str = "vllm@modelsync.local"
    ) -> Dict[str, Any]:
        """Inicializar repositorio ModelSync"""
        response = self.session.post(
            f"{self.base_url}/modelsync/init",
            params={"user_name": user_name, "user_email": user_email}
        )
        response.raise_for_status()
        return response.json()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del servicio"""
        response = self.session.get(f"{self.base_url}/metrics")
        response.raise_for_status()
        return response.json()

class VLLMExperimentManager:
    """Gestor de experimentos para vLLM con ModelSync"""
    
    def __init__(self, client: VLLMClient):
        self.client = client
    
    def run_experiment(
        self,
        experiment_name: str,
        prompts: List[str],
        parameters: Dict[str, Any],
        description: str = ""
    ) -> Dict[str, Any]:
        """Ejecutar un experimento con diferentes parámetros"""
        results = []
        
        for i, prompt in enumerate(prompts):
            try:
                response = self.client.generate(
                    prompt=prompt,
                    **parameters,
                    save_to_version_control=True
                )
                
                results.append({
                    "prompt_index": i,
                    "prompt": prompt,
                    "response": response["text"],
                    "model_version_id": response.get("model_version_id"),
                    "usage": response["usage"],
                    "created": response["created"]
                })
                
            except Exception as e:
                results.append({
                    "prompt_index": i,
                    "prompt": prompt,
                    "error": str(e),
                    "created": datetime.now().isoformat()
                })
        
        # Crear resumen del experimento
        experiment_summary = {
            "experiment_name": experiment_name,
            "description": description,
            "parameters": parameters,
            "total_prompts": len(prompts),
            "successful_generations": len([r for r in results if "error" not in r]),
            "failed_generations": len([r for r in results if "error" in r]),
            "total_tokens": sum(r.get("usage", {}).get("total_tokens", 0) for r in results if "usage" in r),
            "results": results,
            "created": datetime.now().isoformat()
        }
        
        return experiment_summary
    
    def compare_parameters(
        self,
        base_prompts: List[str],
        parameter_sets: List[Dict[str, Any]],
        experiment_name: str = "parameter_comparison"
    ) -> Dict[str, Any]:
        """Comparar diferentes conjuntos de parámetros"""
        comparison_results = []
        
        for i, params in enumerate(parameter_sets):
            param_name = f"param_set_{i+1}"
            experiment_result = self.run_experiment(
                experiment_name=f"{experiment_name}_{param_name}",
                prompts=base_prompts,
                parameters=params,
                description=f"Parameter set {i+1}: {params}"
            )
            
            comparison_results.append({
                "parameter_set": params,
                "parameter_name": param_name,
                "experiment_result": experiment_result
            })
        
        return {
            "comparison_name": experiment_name,
            "base_prompts": base_prompts,
            "parameter_sets": parameter_sets,
            "results": comparison_results,
            "created": datetime.now().isoformat()
        }

# Ejemplo de uso
if __name__ == "__main__":
    client = VLLMClient()
    
    # Verificar salud
    health = client.health_check()
    print(f"Estado del servicio: {health}")
    
    # Verificar estado de ModelSync
    modelsync_status = client.get_modelsync_status()
    print(f"Estado ModelSync: {modelsync_status}")
    
    # Inicializar ModelSync si es necesario
    if modelsync_status["status"] == "not_initialized":
        init_result = client.init_modelsync()
        print(f"Inicialización ModelSync: {init_result}")
    
    # Generar texto
    response = client.generate(
        prompt="Hola, ¿cómo estás?",
        max_tokens=50,
        temperature=0.7
    )
    print(f"Respuesta: {response['text']}")
    print(f"Versión del modelo: {response.get('model_version_id', 'No guardado')}")
    
    # Ejemplo de experimento
    experiment_manager = VLLMExperimentManager(client)
    
    experiment_result = experiment_manager.run_experiment(
        experiment_name="test_experiment",
        prompts=[
            "Cuéntame un chiste",
            "Explica qué es la inteligencia artificial",
            "¿Cuál es la capital de Francia?"
        ],
        parameters={
            "max_tokens": 30,
            "temperature": 0.7,
            "top_p": 0.9
        },
        description="Experimento de prueba con diferentes prompts"
    )
    
    print(f"Experimento completado: {experiment_result['successful_generations']}/{experiment_result['total_prompts']} exitosos")
