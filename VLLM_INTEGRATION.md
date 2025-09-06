# ModelSync vLLM Integration

## 🚀 **Integración Completa de vLLM con ModelSync**

Esta integración permite usar vLLM (Very Large Language Models) con versionado automático en ModelSync, proporcionando un sistema completo para experimentos con modelos de lenguaje.

## 📋 **Características Principales**

### ✅ **API de vLLM Integrada**
- **Servicio FastAPI** dedicado para vLLM
- **Integración automática** con ModelSync
- **Versionado de generaciones** automático
- **Auditoría completa** de todas las operaciones
- **Métricas en tiempo real** del servicio

### ✅ **Gestión de Modelos LLM**
- **Carga dinámica** de modelos
- **Soporte para múltiples modelos** simultáneos
- **Versionado de modelos** en ModelSync
- **Metadatos completos** (parámetros, métricas, uso)

### ✅ **Experimentación Avanzada**
- **Experimentos controlados** con diferentes parámetros
- **Comparación automática** de configuraciones
- **Generación en lote** optimizada
- **Análisis de rendimiento** detallado

### ✅ **CLI Integrado**
- **Comandos específicos** para vLLM
- **Gestión desde terminal** completa
- **Monitoreo en tiempo real** del servicio

## 🛠️ **Instalación y Configuración**

### **1. Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### **2. Iniciar Servicio vLLM**
```bash
# Opción 1: CLI
modelsync llm start

# Opción 2: Python directo
python -m modelsync.llm.vllm_api

# Opción 3: Docker
docker-compose -f docker-compose.vllm.yml up
```

### **3. Verificar Estado**
```bash
modelsync llm_status
```

## 📚 **Uso de la API**

### **Endpoints Principales**

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Información de la API |
| `/health` | GET | Estado del servicio |
| `/models` | GET | Listar modelos cargados |
| `/generate` | POST | Generar texto individual |
| `/generate/batch` | POST | Generar texto en lote |
| `/modelsync/status` | GET | Estado de ModelSync |
| `/modelsync/init` | POST | Inicializar ModelSync |
| `/metrics` | GET | Métricas del servicio |

### **Ejemplo de Generación Individual**
```python
from modelsync.llm.vllm_client import VLLMClient

client = VLLMClient()

response = client.generate(
    prompt="Hola, ¿cómo estás?",
    max_tokens=100,
    temperature=0.7,
    save_to_version_control=True
)

print(response['text'])
print(f"ModelSync ID: {response['model_version_id']}")
```

### **Ejemplo de Generación en Lote**
```python
prompts = [
    "Explica qué es la inteligencia artificial",
    "Cuéntame un chiste",
    "¿Cuál es la capital de Francia?"
]

responses = client.generate_batch(
    prompts=prompts,
    max_tokens=50,
    temperature=0.8
)

for i, response in enumerate(responses):
    print(f"{i+1}. {response['text']}")
```

## 🧪 **Experimentación Avanzada**

### **Gestor de Experimentos**
```python
from modelsync.llm.vllm_client import VLLMExperimentManager

experiment_manager = VLLMExperimentManager(client)

# Ejecutar experimento
experiment_result = experiment_manager.run_experiment(
    experiment_name="temperature_test",
    prompts=["Escribe un poema sobre la tecnología"],
    parameters={
        "max_tokens": 100,
        "temperature": 0.9,
        "top_p": 0.95
    },
    description="Prueba de creatividad con alta temperatura"
)

print(f"Exitosos: {experiment_result['successful_generations']}")
```

### **Comparación de Parámetros**
```python
# Comparar diferentes temperaturas
comparison_result = experiment_manager.compare_parameters(
    base_prompts=["Escribe una historia corta"],
    parameter_sets=[
        {"temperature": 0.3, "max_tokens": 50},  # Conservador
        {"temperature": 0.7, "max_tokens": 50},  # Balanceado
        {"temperature": 1.2, "max_tokens": 50}   # Creativo
    ],
    experiment_name="temperature_comparison"
)
```

## 🖥️ **Comandos CLI**

### **Comandos Básicos**
```bash
# Iniciar servicio vLLM
modelsync llm start

# Verificar estado
modelsync llm_status

# Generar texto
modelsync llm generate --prompt "Hola, ¿cómo estás?" --max-tokens 100

# Ver ayuda
modelsync llm --help
```

### **Parámetros de Generación**
```bash
modelsync llm generate \
  --prompt "Escribe un poema" \
  --max-tokens 200 \
  --temperature 0.8 \
  --model "meta-llama/Meta-Llama-3-8B-Instruct"
```

## 🐳 **Docker y Contenedores**

### **Docker Compose para vLLM**
```bash
# Iniciar todos los servicios
docker-compose -f docker-compose.vllm.yml up

# Solo vLLM API
docker-compose -f docker-compose.vllm.yml up modelsync-vllm

# En segundo plano
docker-compose -f docker-compose.vllm.yml up -d
```

### **Dockerfile Específico**
```dockerfile
FROM nvidia/cuda:11.8-devel-ubuntu20.04
# ... configuración específica para vLLM
```

## 📊 **Monitoreo y Métricas**

### **Métricas Disponibles**
- **Modelos cargados** y su estado
- **Total de requests** procesados
- **Tiempo promedio** de respuesta
- **Uso de memoria** y GPU
- **Actividad reciente** del servicio
- **Integración ModelSync** status

### **Auditoría Completa**
- **Log de todas las generaciones** con metadatos
- **Rastreo de usuarios** y acciones
- **Historial de experimentos** detallado
- **Métricas de rendimiento** por modelo

## 🔧 **Configuración Avanzada**

### **Variables de Entorno**
```bash
export CUDA_VISIBLE_DEVICES=0
export VLLM_USE_MODELSCOPE=False
export PYTHONPATH=/app
```

### **Configuración de Modelos**
```python
# Cargar modelo personalizado
client.load_model("microsoft/DialoGPT-medium")

# Verificar modelos disponibles
models = client.list_models()
```

## 🚀 **Ejemplos Prácticos**

### **1. Ejemplo Básico**
```bash
# Ejecutar ejemplo completo
python examples/vllm_example.py
```

### **2. Integración con ModelSync**
```python
# El versionado es automático
response = client.generate(
    prompt="Tu prompt aquí",
    save_to_version_control=True  # Por defecto True
)

# Ver en ModelSync
modelsync model list
modelsync log
```

### **3. Experimentos de Investigación**
```python
# Configurar experimento científico
experiment_config = {
    "prompts": ["Prompt base para comparar"],
    "parameter_sets": [
        {"temperature": 0.1, "top_p": 0.9},
        {"temperature": 0.5, "top_p": 0.9},
        {"temperature": 1.0, "top_p": 0.9}
    ],
    "repetitions": 3
}

# Ejecutar y analizar
results = run_scientific_experiment(experiment_config)
```

## 🔍 **Troubleshooting**

### **Problemas Comunes**

**1. Servicio no responde**
```bash
# Verificar estado
modelsync llm_status

# Reiniciar servicio
modelsync llm start
```

**2. Modelo no carga**
```bash
# Verificar GPU disponible
nvidia-smi

# Verificar memoria
free -h
```

**3. Error de ModelSync**
```bash
# Inicializar ModelSync
curl -X POST http://localhost:8001/modelsync/init
```

## 📈 **Rendimiento y Optimización**

### **Recomendaciones**
- **GPU con al menos 8GB** de VRAM para modelos grandes
- **SSD rápido** para carga de modelos
- **Memoria RAM suficiente** (16GB+ recomendado)
- **Configurar CUDA** correctamente

### **Monitoreo de Recursos**
```bash
# Ver uso de GPU
nvidia-smi

# Ver métricas del servicio
curl http://localhost:8001/metrics
```

## 🎯 **Casos de Uso**

### **1. Investigación en IA**
- Experimentos controlados con diferentes parámetros
- Comparación sistemática de modelos
- Análisis de rendimiento detallado

### **2. Desarrollo de Aplicaciones**
- Prototipado rápido de funcionalidades LLM
- Testing automatizado de generación
- Versionado de configuraciones

### **3. Producción**
- API escalable para inferencia
- Monitoreo en tiempo real
- Auditoría completa de uso

## 🎉 **Conclusión**

La integración de vLLM con ModelSync proporciona una solución completa para:

- **Experimentación** con modelos de lenguaje
- **Versionado** automático de generaciones
- **Colaboración** en equipos de investigación
- **Producción** escalable y monitoreada

¡Comienza a experimentar con modelos de lenguaje de manera profesional y versionada! 🚀
