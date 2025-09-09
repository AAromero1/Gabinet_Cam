#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema mejorado de tracking con cantidades
"""
import time
import logging
from enhanced_food_detector import EnhancedFoodObjectDetector
import numpy as np
import cv2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def simulate_detections():
    """Simular detecciones para probar el sistema de cantidades"""
    detector = EnhancedFoodObjectDetector(
        model_path="yolov8n.pt",
        confidence_threshold=0.4
    )
    
    print("🧪 PRUEBA DEL SISTEMA DE CANTIDADES")
    print("=" * 50)
    print("Simulando detecciones para verificar el tracking inteligente...")
    
    # Simular detecciones de prueba
    test_detections = [
        # Frame 1: 1 manzana
        [{
            'class_name': 'apple',
            'category': 'fruta',
            'priority': 'high',
            'confidence': 0.85,
            'bbox': (100, 100, 200, 200),
            'area': 10000
        }],
        
        # Frame 2: Misma manzana (debería mantener cantidad 1)
        [{
            'class_name': 'apple',
            'category': 'fruta',
            'priority': 'high',
            'confidence': 0.87,
            'bbox': (105, 105, 205, 205),
            'area': 10000
        }],
        
        # Frame 3: 2 manzanas (debería aumentar cantidad a 2)
        [{
            'class_name': 'apple',
            'category': 'fruta',
            'priority': 'high',
            'confidence': 0.83,
            'bbox': (100, 100, 200, 200),
            'area': 10000
        },
        {
            'class_name': 'apple',
            'category': 'fruta',
            'priority': 'high',
            'confidence': 0.81,
            'bbox': (300, 100, 400, 200),
            'area': 10000
        }],
        
        # Frame 4: 3 manzanas (debería aumentar cantidad a 3)
        [{
            'class_name': 'apple',
            'category': 'fruta',
            'priority': 'high',
            'confidence': 0.84,
            'bbox': (100, 100, 200, 200),
            'area': 10000
        },
        {
            'class_name': 'apple',
            'category': 'fruta',
            'priority': 'high',
            'confidence': 0.82,
            'bbox': (300, 100, 400, 200),
            'area': 10000
        },
        {
            'class_name': 'apple',
            'category': 'fruta',
            'priority': 'high',
            'confidence': 0.86,
            'bbox': (500, 100, 600, 200),
            'area': 10000
        }],
        
        # Frame 5: Agregar 1 banana (nueva categoría)
        [{
            'class_name': 'apple',
            'category': 'fruta',
            'priority': 'high',
            'confidence': 0.84,
            'bbox': (100, 100, 200, 200),
            'area': 10000
        },
        {
            'class_name': 'apple',
            'category': 'fruta',
            'priority': 'high',
            'confidence': 0.82,
            'bbox': (300, 100, 400, 200),
            'area': 10000
        },
        {
            'class_name': 'apple',
            'category': 'fruta',
            'priority': 'high',
            'confidence': 0.86,
            'bbox': (500, 100, 600, 200),
            'area': 10000
        },
        {
            'class_name': 'banana',
            'category': 'fruta',
            'priority': 'high',
            'confidence': 0.88,
            'bbox': (100, 300, 200, 400),
            'area': 10000
        }]
    ]
    
    # Procesar cada frame de prueba
    for frame_num, detections in enumerate(test_detections, 1):
        print(f"\n📋 FRAME {frame_num}")
        print(f"Detecciones: {len(detections)}")
        for det in detections:
            print(f"  • {det['class_name']} (confianza: {det['confidence']:.2f})")
        
        # Actualizar el tracking
        detector._update_tracked_objects(detections)
        
        # Mostrar estado actual
        print(f"\n🎯 Estado del tracking:")
        for object_key, obj_info in detector._tracked_objects.items():
            detection = obj_info['detection']
            status = "✅ REG" if obj_info['registered'] else "⏳ PEND"
            print(f"  • {detection['class_name']}: {obj_info['quantity']} unidades "
                  f"({status}, detecciones: {obj_info['total_detections']})")
        
        # Simular 30 frames de la misma detección para activar registro
        if frame_num == 3:  # En el frame 3 vamos a simular muchas detecciones
            print("\n⏰ Simulando 30 frames adicionales para activar registro...")
            for _ in range(30):
                detector._update_tracked_objects(detections)
        
        time.sleep(1)  # Pausa para observar
    
    # Mostrar estadísticas finales
    print("\n📊 ESTADÍSTICAS FINALES")
    detector._print_tracking_stats()
    
    return detector

def test_quantity_system():
    """Probar específicamente el sistema de cantidades"""
    print("\n🔬 PRUEBA ESPECÍFICA DEL SISTEMA DE CANTIDADES")
    print("=" * 60)
    
    detector = simulate_detections()
    
    print("\n✅ Prueba completada!")
    print("\nVerifica que:")
    print("1. Las manzanas se agruparon bajo un solo ID")
    print("2. La cantidad aumentó de 1 a 2 a 3")
    print("3. La banana se registró por separado")
    print("4. No se crearon múltiples IDs para el mismo tipo de objeto")

def main():
    """Función principal de prueba"""
    try:
        test_quantity_system()
    except Exception as e:
        logger.error(f"Error en la prueba: {e}")

if __name__ == "__main__":
    main()
