#!/usr/bin/env python3
"""
Script de prueba para verificar que el sistema de detección de videos
registre correctamente los elementos en Google Sheets/Excel.
"""

import os
import sys
import logging
from enhanced_food_detector import EnhancedFoodObjectDetector

# Configurar logging detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_video_to_excel_integration():
    """
    Prueba la integración completa de video con Excel/Google Sheets
    """
    print("🎬 PRUEBA: DETECCIÓN DE VIDEO CON REGISTRO EN EXCEL")
    print("=" * 60)
    
    # Verificar si hay videos de prueba disponibles
    video_files = []
    for ext in ['.mp4', '.avi', '.mov', '.mkv']:
        for file in os.listdir('.'):
            if file.lower().endswith(ext):
                video_files.append(file)
    
    if not video_files:
        print("⚠️ No se encontraron videos de prueba en el directorio actual")
        print("📝 Para probar, coloca un video (.mp4, .avi, .mov, .mkv) en este directorio")
        return False
    
    print(f"📹 Videos encontrados: {', '.join(video_files)}")
    video_path = video_files[0]
    output_path = f"test_detected_{os.path.splitext(video_path)[0]}.mp4"
    
    print(f"📥 Video de entrada: {video_path}")
    print(f"📤 Video de salida: {output_path}")
    print("-" * 60)
    
    try:
        # Crear detector con configuración específica para prueba
        detector = EnhancedFoodObjectDetector(
            model_path="yolov8n.pt",
            confidence_threshold=0.3,  # Umbral más bajo para detectar más objetos
            video_source=video_path,
            output_video_path=output_path
        )
        
        # Verificar conexión a Google Sheets ANTES de procesar
        print("🔍 VERIFICACIÓN INICIAL:")
        print(f"  • Google Sheets: {'✅ CONECTADO' if detector.sheets_manager.is_connected else '❌ DESCONECTADO'}")
        
        if not detector.sheets_manager.is_connected:
            print("❌ ERROR: Google Sheets no está conectado")
            print("   Verifica el archivo 'calm-segment-credentials.json'")
            return False
        
        # Obtener información del spreadsheet
        try:
            sheet_info = detector.sheets_manager.get_spreadsheet_info()
            print(f"  • Documento: {sheet_info.get('title', 'N/A')}")
            print(f"  • Registros actuales: {sheet_info.get('data_rows', 0)}")
            print(f"  • URL: {detector.sheets_manager.get_spreadsheet_url()}")
        except Exception as e:
            print(f"  • Error obteniendo info del sheet: {e}")
        
        print("-" * 60)
        print("🚀 INICIANDO PROCESAMIENTO DE VIDEO...")
        print("   Los elementos detectados DEBERÍAN aparecer en el Excel/Google Sheets")
        print("-" * 60)
        
        # Ejecutar detección
        detector.run_enhanced_detection()
        
        # Verificar resultados
        print("\n" + "=" * 60)
        print("📊 RESULTADOS DE LA PRUEBA")
        print("=" * 60)
        
        # Verificar si se creó el video de salida
        if os.path.exists(output_path):
            print(f"✅ Video de salida creado: {output_path}")
        else:
            print("❌ No se creó el video de salida")
        
        # Verificar estado final del tracking
        tracked_count = len(detector._tracked_objects)
        registered_count = sum(1 for obj in detector._tracked_objects.values() if obj['registered'])
        
        print(f"🎯 Objetos tracked: {tracked_count}")
        print(f"📦 Objetos registrados en Excel: {registered_count}")
        
        if registered_count > 0:
            print("✅ ¡ÉXITO! Se registraron elementos en Excel/Google Sheets")
            print("\n📋 ELEMENTOS REGISTRADOS:")
            for obj_key, obj_info in detector._tracked_objects.items():
                if obj_info['registered']:
                    item_name = obj_info['detection']['class_name']
                    item_id = obj_info.get('item_id', 'N/A')
                    quantity = obj_info['quantity']
                    print(f"  • {item_name} x{quantity} (ID: {item_id})")
        else:
            print("⚠️ No se registraron elementos en Excel")
            print("   Posibles causas:")
            print("   - No se detectaron objetos suficientes")
            print("   - Los objetos no cumplieron el umbral de confirmación")
            print("   - Problema de conexión con Google Sheets")
        
        # Mostrar información de Google Sheets al final
        try:
            final_info = detector.sheets_manager.get_spreadsheet_info()
            final_rows = final_info.get('data_rows', 0)
            print(f"\n📊 Registros finales en Excel: {final_rows}")
        except Exception as e:
            print(f"❌ Error verificando estado final: {e}")
        
        return registered_count > 0
        
    except Exception as e:
        logger.error(f"❌ Error durante la prueba: {e}")
        return False

def main():
    """Función principal"""
    print("🎯 PRUEBA DE INTEGRACIÓN: VIDEO → EXCEL/GOOGLE SHEETS")
    print("Este script verifica que los elementos detectados en videos")
    print("se registren correctamente en el Excel/Google Sheets")
    print()
    
    success = test_video_to_excel_integration()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 PRUEBA EXITOSA: El sistema registra elementos de video en Excel")
    else:
        print("❌ PRUEBA FALLIDA: Revisar configuración y logs")
    print("=" * 60)

if __name__ == "__main__":
    main()
