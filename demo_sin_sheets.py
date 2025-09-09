#!/usr/bin/env python3
"""
Demo del detector sin Google Sheets para probar que la detección funciona
"""

import sys
import os
import time
from enhanced_food_detector import EnhancedFoodObjectDetector

def main():
    print("🎬 DEMO: DETECTOR SIN GOOGLE SHEETS")
    print("Este modo permite probar la detección sin conexión a Google Sheets")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("❌ Uso: python demo_sin_sheets.py <video.mp4>")
        print("📝 Ejemplo: python demo_sin_sheets.py mi_video.mp4")
        return
    
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        print(f"❌ Video no encontrado: {video_path}")
        return
    
    # Generar nombre para video de salida
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_path = f"{video_name}_detecciones_local.mp4"
    
    print(f"📹 Video entrada: {video_path}")
    print(f"📤 Video salida: {output_path}")
    print("📊 Modo: Solo detección local (sin Google Sheets)")
    print("=" * 60)
    
    # Crear detector
    detector = EnhancedFoodObjectDetector(
        model_path="yolov8n.pt",
        confidence_threshold=0.3,
        video_source=video_path,
        output_video_path=output_path
    )
    
    # Mostrar estado
    if detector.sheets_manager.is_connected:
        print("✅ Google Sheets conectado - Los elementos se registrarán")
    else:
        print("⚠️ Google Sheets desconectado - Solo detección local")
        print("   Las detecciones se mostrarán en consola y video")
    
    print("=" * 60)
    print("🚀 INICIANDO PROCESAMIENTO...")
    
    # Procesar video
    detector.run_enhanced_detection()
    
    # Mostrar resultados
    print("\n" + "=" * 60)
    print("📊 RESULTADOS FINALES")
    print("=" * 60)
    
    tracked_objects = len(detector._tracked_objects)
    print(f"🎯 Total objetos detectados y tracked: {tracked_objects}")
    
    if tracked_objects > 0:
        print("\n📋 OBJETOS DETECTADOS:")
        for obj_key, obj_info in detector._tracked_objects.items():
            name = obj_info['detection']['class_name']
            category = obj_info['detection']['category']
            quantity = obj_info['quantity']
            confidence = obj_info['avg_confidence']
            status = "✅ REGISTRADO" if obj_info['registered'] else "⏳ DETECTADO"
            
            print(f"  • {name} ({category})")
            print(f"    - Estado: {status}")
            print(f"    - Cantidad: {quantity}")
            print(f"    - Confianza: {confidence:.3f}")
            
            if obj_info.get('item_id'):
                print(f"    - ID en Excel: {obj_info['item_id']}")
            print()
    else:
        print("ℹ️ No se detectaron objetos de interés en el video")
        print("   Posibles causas:")
        print("   - El video no contiene alimentos/objetos detectables")
        print("   - Umbral de confianza muy alto")
        print("   - Video muy corto para confirmación de objetos")
    
    if os.path.exists(output_path):
        print(f"🎬 Video procesado guardado: {output_path}")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
