#!/usr/bin/env python3
"""
Script de ejemplo para demostrar el detector con videos
"""
import os
import sys
from enhanced_food_detector import EnhancedFoodObjectDetector
import cv2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_video():
    """Crear un video de ejemplo simple para demostración"""
    try:
        # Crear un video simple con forma circular que simula un objeto
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logger.warning("No se puede acceder a la cámara para crear video de ejemplo")
            return None
        
        # Configurar grabación
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('sample_video.mp4', fourcc, 20.0, (640, 480))
        
        logger.info("Grabando video de ejemplo... Presiona 'q' para terminar")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Redimensionar para consistencia
            frame = cv2.resize(frame, (640, 480))
            
            # Agregar texto informativo
            cv2.putText(frame, "Video de ejemplo - Muestra objetos comestibles", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Presiona 'q' para terminar grabacion", 
                       (10, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            out.write(frame)
            cv2.imshow('Grabando video de ejemplo', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        
        logger.info("✅ Video de ejemplo creado: sample_video.mp4")
        return "sample_video.mp4"
        
    except Exception as e:
        logger.error(f"Error creando video de ejemplo: {e}")
        return None

def run_video_detection_demo():
    """Ejecutar demostración completa del detector de video"""
    print("🎬 DEMOSTRACIÓN DEL DETECTOR DE VIDEO")
    print("=" * 50)
    
    # Buscar videos existentes
    video_files = [f for f in os.listdir('.') if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    
    if video_files:
        print("📁 Videos encontrados:")
        for i, video in enumerate(video_files, 1):
            print(f"  {i}. {video}")
        
        choice = input("\n¿Usar video existente? (número) o 'n' para crear nuevo: ")
        
        if choice.isdigit() and 1 <= int(choice) <= len(video_files):
            video_path = video_files[int(choice) - 1]
        else:
            video_path = create_sample_video()
    else:
        print("📹 No se encontraron videos. Creando video de ejemplo...")
        video_path = create_sample_video()
    
    if not video_path or not os.path.exists(video_path):
        print("❌ No se pudo obtener video para procesar")
        return
    
    # Configurar detección
    output_path = f"{os.path.splitext(video_path)[0]}_detected.mp4"
    confidence = 0.4
    
    print(f"\n🎯 Configuración:")
    print(f"  📹 Video entrada: {video_path}")
    print(f"  💾 Video salida: {output_path}")
    print(f"  🎯 Confianza: {confidence}")
    
    input("\n🚀 Presiona Enter para comenzar detección...")
    
    try:
        # Crear detector configurado para video
        detector = EnhancedFoodObjectDetector(
            model_path="yolov8n.pt",
            confidence_threshold=confidence,
            video_source=video_path,
            output_video_path=output_path
        )
        
        print("\n🔍 Iniciando detección...")
        detector.run_enhanced_detection()
        
        print(f"\n✅ ¡Procesamiento completado!")
        print(f"🎬 Video con detecciones guardado en: {output_path}")
        
        # Preguntar si quiere reproducir el resultado
        play = input("\n🎥 ¿Reproducir video resultado? (y/n): ")
        if play.lower() == 'y':
            play_video(output_path)
        
    except Exception as e:
        logger.error(f"❌ Error en la demostración: {e}")

def play_video(video_path: str):
    """Reproducir un video"""
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            logger.error(f"No se puede abrir el video: {video_path}")
            return
        
        logger.info(f"Reproduciendo: {video_path}")
        logger.info("Presiona 'q' para salir, ESPACIO para pausar")
        
        paused = False
        
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    logger.info("Video terminado")
                    break
            
            cv2.imshow(f'Reproduciendo: {os.path.basename(video_path)}', frame)
            
            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' '):  # Espacio para pausar
                paused = not paused
                logger.info("Video pausado" if paused else "Video reanudado")
        
        cap.release()
        cv2.destroyAllWindows()
        
    except Exception as e:
        logger.error(f"Error reproduciendo video: {e}")

def main():
    """Función principal"""
    try:
        run_video_detection_demo()
    except KeyboardInterrupt:
        print("\n❌ Demostración cancelada por el usuario")
    except Exception as e:
        logger.error(f"Error en la demostración: {e}")

if __name__ == "__main__":
    main()
