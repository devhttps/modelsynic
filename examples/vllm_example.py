#!/usr/bin/env python3
"""
Ejemplo de uso de vLLM con ModelSync
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modelsync.llm.vllm_client import VLLMClient, VLLMExperimentManager

def demonstrate_vllm_integration():
    """Demostrar la integración de vLLM con ModelSync"""
    print("🚀 ModelSync vLLM Integration Demo")
    print("=" * 50)
    
    # Inicializar cliente
    client = VLLMClient()
    
    # 1. Verificar estado del servicio
    print("\n1️⃣ Verificando estado del servicio...")
    try:
        health = client.health_check()
        print(f"✅ Estado del servicio: {health['status']}")
        print(f"📊 Modelos cargados: {health['models_loaded']}")
        print(f"🔗 ModelSync: {health['modelsync_status']}")
    except Exception as e:
        print(f"❌ Error conectando al servicio: {e}")
        print("💡 Asegúrate de que el servicio esté ejecutándose:")
        print("   modelsync llm start")
        return
    
    # 2. Inicializar ModelSync si es necesario
    print("\n2️⃣ Configurando ModelSync...")
    modelsync_status = client.get_modelsync_status()
    if modelsync_status["status"] == "not_initialized":
        print("🔧 Inicializando repositorio ModelSync...")
        init_result = client.init_modelsync()
        print(f"✅ {init_result['message']}")
    else:
        print("✅ ModelSync ya está inicializado")
    
    # 3. Listar modelos disponibles
    print("\n3️⃣ Modelos disponibles:")
    models = client.list_models()
    for model in models:
        print(f"  • {model['name']} ({model['status']})")
        if model.get('version_control_id'):
            print(f"    📝 Versión en ModelSync: {model['version_control_id']}")
    
    # 4. Generar texto simple
    print("\n4️⃣ Generación de texto simple...")
    try:
        response = client.generate(
            prompt="Hola, ¿cómo estás? Cuéntame algo interesante sobre la inteligencia artificial.",
            max_tokens=100,
            temperature=0.7,
            save_to_version_control=True
        )
        
        print(f"🤖 Respuesta generada:")
        print(f"   {response['text']}")
        print(f"📊 Uso de tokens: {response['usage']}")
        if response.get('model_version_id'):
            print(f"💾 Guardado en ModelSync: {response['model_version_id']}")
    except Exception as e:
        print(f"❌ Error en generación: {e}")
    
    # 5. Generación en lote
    print("\n5️⃣ Generación en lote...")
    prompts = [
        "Explica qué es el machine learning en una frase",
        "¿Cuál es la diferencia entre AI y ML?",
        "Dame un consejo para programadores"
    ]
    
    try:
        batch_responses = client.generate_batch(
            prompts=prompts,
            max_tokens=50,
            temperature=0.8,
            save_to_version_control=True
        )
        
        print(f"📦 Generadas {len(batch_responses)} respuestas:")
        for i, response in enumerate(batch_responses):
            print(f"  {i+1}. {response['text'][:100]}...")
            if response.get('model_version_id'):
                print(f"     💾 ModelSync ID: {response['model_version_id']}")
    except Exception as e:
        print(f"❌ Error en generación por lotes: {e}")
    
    # 6. Experimento avanzado
    print("\n6️⃣ Ejecutando experimento avanzado...")
    experiment_manager = VLLMExperimentManager(client)
    
    try:
        experiment_result = experiment_manager.run_experiment(
            experiment_name="temperature_comparison",
            prompts=[
                "Escribe un poema sobre la tecnología",
                "Explica el concepto de recursión",
                "¿Qué es la programación orientada a objetos?"
            ],
            parameters={
                "max_tokens": 80,
                "temperature": 0.9,
                "top_p": 0.95
            },
            description="Experimento comparando diferentes temperaturas de generación"
        )
        
        print(f"🧪 Experimento completado:")
        print(f"   Prompts procesados: {experiment_result['total_prompts']}")
        print(f"   Generaciones exitosas: {experiment_result['successful_generations']}")
        print(f"   Tokens totales: {experiment_result['total_tokens']}")
        
        # Mostrar algunas respuestas
        print(f"\n📝 Algunas respuestas del experimento:")
        for i, result in enumerate(experiment_result['results'][:2]):
            if 'error' not in result:
                print(f"  {i+1}. {result['response'][:150]}...")
    except Exception as e:
        print(f"❌ Error en experimento: {e}")
    
    # 7. Comparación de parámetros
    print("\n7️⃣ Comparación de parámetros...")
    try:
        comparison_result = experiment_manager.compare_parameters(
            base_prompts=["Escribe una historia corta sobre un robot"],
            parameter_sets=[
                {"temperature": 0.3, "max_tokens": 50},  # Más conservador
                {"temperature": 0.7, "max_tokens": 50},  # Balanceado
                {"temperature": 1.2, "max_tokens": 50}   # Más creativo
            ],
            experiment_name="temperature_comparison"
        )
        
        print(f"🔬 Comparación completada:")
        print(f"   Conjuntos de parámetros: {len(comparison_result['parameter_sets'])}")
        print(f"   Prompts base: {len(comparison_result['base_prompts'])}")
        
        for i, result in enumerate(comparison_result['results']):
            param_set = result['parameter_set']
            experiment = result['experiment_result']
            print(f"  Parámetro {i+1} (temp={param_set['temperature']}):")
            print(f"    Exitosos: {experiment['successful_generations']}/{experiment['total_prompts']}")
            print(f"    Tokens: {experiment['total_tokens']}")
    except Exception as e:
        print(f"❌ Error en comparación: {e}")
    
    # 8. Métricas finales
    print("\n8️⃣ Métricas del servicio...")
    try:
        metrics = client.get_metrics()
        print(f"📊 Métricas:")
        print(f"   Modelos cargados: {metrics['models_loaded']}")
        print(f"   Total de requests: {metrics['total_requests']}")
        print(f"   Actividad reciente: {metrics['recent_activity']}")
        print(f"   Integración ModelSync: {metrics['modelsync_integration']}")
    except Exception as e:
        print(f"❌ Error obteniendo métricas: {e}")
    
    print("\n🎉 Demo de vLLM con ModelSync completado!")
    print("\n📚 Lo que se demostró:")
    print("   ✅ Integración completa con ModelSync")
    print("   ✅ Generación de texto individual y en lote")
    print("   ✅ Versionado automático de generaciones")
    print("   ✅ Experimentos y comparaciones de parámetros")
    print("   ✅ Auditoría y métricas")
    print("   ✅ Gestión de modelos LLM")
    
    print("\n🚀 Próximos pasos:")
    print("   • Usar CLI: modelsync llm generate --prompt 'tu prompt aquí'")
    print("   • Ver estado: modelsync llm_status")
    print("   • Iniciar servicio: modelsync llm start")

if __name__ == "__main__":
    demonstrate_vllm_integration()
