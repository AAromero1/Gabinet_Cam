#!/usr/bin/env python3
"""
Test para verificar la integración completa del sistema de inventario
con Google Sheets usando la estructura sophisticada de despensa.

Autor: GitHub Copilot
"""

import time
import logging
from google_sheets_integration import GoogleSheetsManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_google_sheets_integration():
    """Probar la integración completa con Google Sheets"""
    print("🧪 === PRUEBA DE INTEGRACIÓN GOOGLE SHEETS ===")
    
    # Inicializar gestor
    sheets_manager = GoogleSheetsManager()
    
    if not sheets_manager.get_connection_status():
        print("❌ No se pudo conectar a Google Sheets")
        return False
    
    print("✅ Conexión a Google Sheets exitosa")
    
    # Mostrar información del spreadsheet
    info = sheets_manager.get_spreadsheet_info()
    print(f"📊 Spreadsheet: {info.get('title', 'N/A')}")
    print(f"🔗 URL: {info.get('url', 'N/A')}")
    
    # Probar detecciones simuladas
    test_detections = [
        ("galletas", 0.85, "Detección de galletas con alta confianza"),
        ("lata", 0.92, "Lata de bebida detectada"),
        ("bebida_contenedor", 0.78, "Contenedor de bebida identificado"),
        ("galletas", 0.88, "Segunda detección de galletas"),
        ("chocolate", 0.82, "Chocolate detectado")
    ]
    
    print("\n🔍 === PROBANDO DETECCIONES ===")
    for item_name, confidence, info in test_detections:
        print(f"\n📝 Registrando: {item_name} (confianza: {confidence:.2f})")
        success = sheets_manager.log_detection(item_name, confidence, info)
        if success:
            print(f"✅ {item_name} registrado exitosamente")
        else:
            print(f"❌ Error registrando {item_name}")
        
        # Pausa breve entre detecciones
        time.sleep(1)
    
    print("\n📊 === INFORMACIÓN FINAL ===")
    final_info = sheets_manager.get_spreadsheet_info()
    print(f"📈 Filas de datos: {final_info.get('data_rows', 0)}")
    
    return True

def test_detection_tracker():
    """Probar el sistema de tracking de detecciones"""
    print("\n🎯 === PRUEBA DE DETECTION TRACKER ===")
    
    from google_sheets_integration import DetectionTracker
    
    # Crear tracker
    tracker = DetectionTracker(stability_frames=5)  # Usar menos frames para prueba
    
    # Simular secuencia de detecciones
    test_sequence = [
        # Frame 1-3: galletas aparecen
        [{"class_name": "galletas", "confidence": 0.85, "bbox": [100, 100, 200, 200], "area": 10000, "category": "Dulces"}],
        [{"class_name": "galletas", "confidence": 0.87, "bbox": [102, 101, 202, 201], "area": 10100, "category": "Dulces"}],
        [{"class_name": "galletas", "confidence": 0.89, "bbox": [99, 99, 199, 199], "area": 10000, "category": "Dulces"}],
        
        # Frame 4-8: galletas continúan + lata aparece
        [
            {"class_name": "galletas", "confidence": 0.86, "bbox": [101, 100, 201, 200], "area": 10000, "category": "Dulces"},
            {"class_name": "lata", "confidence": 0.92, "bbox": [300, 150, 350, 220], "area": 3500, "category": "Bebidas"}
        ],
        [
            {"class_name": "galletas", "confidence": 0.88, "bbox": [100, 101, 200, 201], "area": 10000, "category": "Dulces"},
            {"class_name": "lata", "confidence": 0.90, "bbox": [301, 151, 351, 221], "area": 3500, "category": "Bebidas"}
        ],
        [
            {"class_name": "galletas", "confidence": 0.85, "bbox": [99, 100, 199, 200], "area": 10000, "category": "Dulces"},
            {"class_name": "lata", "confidence": 0.94, "bbox": [299, 149, 349, 219], "area": 3500, "category": "Bebidas"}
        ],
        [
            {"class_name": "galletas", "confidence": 0.87, "bbox": [100, 99, 200, 199], "area": 10000, "category": "Dulces"},
            {"class_name": "lata", "confidence": 0.91, "bbox": [300, 150, 350, 220], "area": 3500, "category": "Bebidas"}
        ],
        [
            {"class_name": "galletas", "confidence": 0.86, "bbox": [101, 100, 201, 200], "area": 10000, "category": "Dulces"},
            {"class_name": "lata", "confidence": 0.93, "bbox": [302, 152, 352, 222], "area": 3500, "category": "Bebidas"}
        ],
        
        # Frame 9-12: solo lata (galletas desaparecen)
        [{"class_name": "lata", "confidence": 0.89, "bbox": [301, 150, 351, 220], "area": 3500, "category": "Bebidas"}],
        [{"class_name": "lata", "confidence": 0.91, "bbox": [300, 151, 350, 221], "area": 3500, "category": "Bebidas"}],
        [{"class_name": "lata", "confidence": 0.88, "bbox": [299, 149, 349, 219], "area": 3500, "category": "Bebidas"}],
        [{"class_name": "lata", "confidence": 0.90, "bbox": [301, 150, 351, 220], "area": 3500, "category": "Bebidas"}],
        
        # Frame 13-17: nada (lata desaparece)
        [], [], [], [], []
    ]
    
    print(f"🎬 Simulando {len(test_sequence)} frames...")
    
    for frame_num, detections in enumerate(test_sequence, 1):
        print(f"Frame {frame_num}: {len(detections)} detecciones")
        tracker.update(detections)
        
        # Mostrar estadísticas cada 5 frames
        if frame_num % 5 == 0:
            stats = tracker.get_stats()
            print(f"  📊 Stats: {stats['active_objects']} activos, {stats['sent_objects']} enviados")
        
        time.sleep(0.1)  # Pausa breve
    
    print("\n📈 === ESTADÍSTICAS FINALES ===")
    final_stats = tracker.get_stats()
    print(f"Frames procesados: {final_stats['frame_count']}")
    print(f"Objetos activos: {final_stats['active_objects']}")
    print(f"Objetos enviados: {final_stats['sent_objects']}")
    print(f"Conexión Sheets: {final_stats['sheets_connected']}")
    
    return True

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas completas del sistema de inventario")
    
    # Probar conexión y registro básico
    success1 = test_google_sheets_integration()
    
    # Probar sistema de tracking
    success2 = test_detection_tracker()
    
    if success1 and success2:
        print("\n🎉 ¡Todas las pruebas completadas exitosamente!")
        print("✅ El sistema de inventario está listo para usar")
    else:
        print("\n⚠️ Algunas pruebas fallaron")
    
    print(f"\n📋 Revisa tu Google Sheets para ver los resultados")

if __name__ == "__main__":
    main()
