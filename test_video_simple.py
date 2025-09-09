#!/usr/bin/env python3
"""
Script directo para procesar un video y verificar que se agregue al Excel
"""

import sys
import os
from enhanced_food_detector import EnhancedFoodObjectDetector

def main():
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("❌ Uso: python test_video_simple.py <ruta_del_video>")
        print("📝 Ejemplo: python test_video_simple.py mi_video.mp4")
        return
    
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        print(f"❌ Video no encontrado: {video_path}")
        return
    
    # Generar nombre para video de salida
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_path = f"{video_name}_con_detecciones.mp4"
    
    print("🎬 PROCESAMIENTO DE VIDEO CON REGISTRO EN EXCEL")
    print("=" * 50)
    print(f"📥 Video entrada: {video_path}")
    print(f"📤 Video salida: {output_path}")
    print("=" * 50)
    
    # Crear detector
    detector = EnhancedFoodObjectDetector(
        model_path="yolov8n.pt",
        confidence_threshold=0.3,
        video_source=video_path,
        output_video_path=output_path
    )
    
    # Verificar Google Sheets
    if detector.sheets_manager.is_connected:
        print("✅ Google Sheets CONECTADO - Los elementos SÍ se agregarán al Excel")
        try:
            sheet_info = detector.sheets_manager.get_spreadsheet_info()
            print(f"📊 Documento: {sheet_info.get('title', 'N/A')}")
            print(f"🔗 URL: {detector.sheets_manager.get_spreadsheet_url()}")
        except:
            pass
    else:
        print("❌ Google Sheets DESCONECTADO - Los elementos NO se agregarán al Excel")
        print("   Verifica el archivo calm-segment-credentials.json")
        return
    
    print("=" * 50)
    print("🚀 INICIANDO PROCESAMIENTO...")
    
    # Procesar video
    detector.run_enhanced_detection()
    
    # Mostrar resultados
    print("\n" + "=" * 50)
    print("📊 RESULTADOS")
    print("=" * 50)
    
    tracked_objects = len(detector._tracked_objects)
    registered_objects = sum(1 for obj in detector._tracked_objects.values() if obj['registered'])
    
    print(f"🎯 Objetos detectados: {tracked_objects}")
    print(f"📦 Objetos agregados al Excel: {registered_objects}")
    
    if registered_objects > 0:
        print("\n✅ ÉXITO - Se agregaron elementos al Excel:")
        for obj_key, obj_info in detector._tracked_objects.items():
            if obj_info['registered']:
                name = obj_info['detection']['class_name']
                quantity = obj_info['quantity']
                item_id = obj_info.get('item_id', 'N/A')
                print(f"  • {name} x{quantity} (ID: {item_id})")
    else:
        print("⚠️ No se agregaron elementos al Excel")
        print("Posibles causas:")
        print("- El video no tiene objetos detectables")
        print("- Los objetos no duraron suficientes frames")
        print("- Umbral de confianza muy alto")
    
    if os.path.exists(output_path):
        print(f"\n🎬 Video procesado guardado: {output_path}")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
