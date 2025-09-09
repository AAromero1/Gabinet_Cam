#!/usr/bin/env python3
"""
Script para detectar objetos en videos usando el detector mejorado
"""
import os
import sys
from enhanced_food_detector import EnhancedFoodObjectDetector
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_video(video_path: str, output_path: str = None, confidence: float = 0.4):
    """
    Procesar un video con detección de objetos
    
    Args:
        video_path: Ruta del video de entrada
        output_path: Ruta del video de salida (opcional)
        confidence: Umbral de confianza
    """
    # Verificar que el archivo de video existe
    if not os.path.exists(video_path):
        logger.error(f"❌ El archivo de video no existe: {video_path}")
        return False
    
    # Generar nombre de salida automáticamente si no se proporciona
    if not output_path:
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = f"{video_name}_detected.mp4"
    
    print("🎬 DETECTOR DE VIDEO - ALIMENTOS Y OBJETOS")
    print("=" * 50)
    print(f"📹 Video de entrada: {video_path}")
    print(f"💾 Video de salida: {output_path}")
    print(f"🎯 Umbral de confianza: {confidence}")
    print("=" * 50)
    
    try:
        # Crear detector
        detector = EnhancedFoodObjectDetector(
            model_path="yolov8n.pt",
            confidence_threshold=confidence,
            video_source=video_path,
            output_video_path=output_path
        )
        
        # Procesar video
        detector.run_enhanced_detection()
        
        print("\n✅ Procesamiento completado!")
        print(f"📁 Video guardado en: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error procesando video: {e}")
        return False

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("🎬 DETECTOR DE VIDEO - USO:")
        print("-" * 30)
        print("python video_detector.py <video_entrada> [video_salida] [confianza]")
        print("\nEjemplos:")
        print("  python video_detector.py mi_video.mp4")
        print("  python video_detector.py mi_video.mp4 resultado.mp4")
        print("  python video_detector.py mi_video.mp4 resultado.mp4 0.5")
        print("\nFormatos soportados: .mp4, .avi, .mov, .mkv, .webm")
        return
    
    # Obtener argumentos
    video_input = sys.argv[1]
    video_output = sys.argv[2] if len(sys.argv) > 2 else None
    confidence = float(sys.argv[3]) if len(sys.argv) > 3 else 0.4
    
    # Procesar video
    success = process_video(video_input, video_output, confidence)
    
    if success:
        print("\n🎉 ¡Procesamiento exitoso!")
        if video_output:
            print(f"🎬 Puedes ver el resultado en: {video_output}")
    else:
        print("\n❌ Error en el procesamiento")
        sys.exit(1)

if __name__ == "__main__":
    main()
