#!/usr/bin/env python3
"""
Demo avanzado del detector de alimentos con múltiples funciones
"""

import cv2
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from utils import *
from ultralytics import YOLO
import time
from collections import deque

class AdvancedFoodDetector:
    """Detector de alimentos con funciones avanzadas"""
    
    def __init__(self):
        # Configurar logging
        setup_logging(Config.LOG_LEVEL, Config.LOG_FORMAT)
        self.logger = logging.getLogger(__name__)
        
        # Crear directorios necesarios
        Config.create_directories()
        
        # Inicializar modelo
        self.model = YOLO(Config.MODEL_PATH)
        self.logger.info(f"Modelo cargado: {Config.MODEL_PATH}")
        
        # Variables de estado
        self.frame_times = deque(maxlen=60)  # Para calcular FPS
        self.detections_history = deque(maxlen=300)  # Historial de 10 segundos aprox
        self.current_fps = 0.0
        self.frame_count = 0
        self.paused = False
        self.show_stats = True
        
        # Información del modelo
        model_info = Config.get_model_info()
        self.logger.info(f"Modelo info: {model_info}")
    
    def run_demo(self):
        """Ejecutar demo completo"""
        # Verificar cámaras disponibles
        available_cameras = get_available_cameras()
        if not available_cameras:
            print("❌ No se encontraron cámaras disponibles")
            return
        
        print(f"📷 Cámaras disponibles: {available_cameras}")
        camera_index = available_cameras[0]
        
        # Inicializar cámara
        cap = cv2.VideoCapture(camera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.CAMERA_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.CAMERA_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, Config.CAMERA_FPS)
        
        if not cap.isOpened():
            print("❌ No se pudo abrir la cámara")
            return
        
        print("🚀 Demo iniciado!")
        self._print_controls()
        
        try:
            while True:
                if not self.paused:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Procesar frame
                    processed_frame = self._process_frame(frame)
                    
                else:
                    # En pausa, solo mostrar último frame
                    processed_frame = self._add_pause_indicator(processed_frame)
                
                # Mostrar frame
                cv2.imshow('🍎 Detector de Alimentos Avanzado', processed_frame)
                
                # Manejar teclas
                key = cv2.waitKey(1) & 0xFF
                if not self._handle_key(key, processed_frame):
                    break
                    
        except KeyboardInterrupt:
            print("\n⚠️ Demo interrumpido por el usuario")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("✅ Demo finalizado")
    
    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Procesar un frame completo"""
        current_time = time.time()
        self.frame_times.append(current_time)
        self.frame_count += 1
        
        # Calcular FPS
        self.current_fps = calculate_fps(list(self.frame_times))
        
        # Redimensionar si es necesario
        frame = resize_frame(frame, Config.CAMERA_WIDTH, Config.CAMERA_HEIGHT)
        
        # Detectar alimentos
        detections = self._detect_foods(frame)
        self.detections_history.append(detections)
        
        # Crear overlay de detecciones
        processed_frame = create_detection_overlay(frame, detections, Config.CLASS_COLORS)
        
        # Añadir información
        if self.show_stats:
            processed_frame = self._add_stats_panel(processed_frame, detections)
        
        # Añadir controles
        processed_frame = self._add_controls_info(processed_frame)
        
        return processed_frame
    
    def _detect_foods(self, frame: np.ndarray) -> List[Dict]:
        """Detectar alimentos en el frame"""
        detections = []
        
        try:
            results = self.model(frame, verbose=False)
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        class_id = int(box.cls)
                        confidence = float(box.conf)
                        
                        # Filtrar solo alimentos con confianza suficiente
                        if (class_id in Config.FOOD_CLASSES and 
                            confidence >= Config.CONFIDENCE_THRESHOLD):
                            
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            
                            detection = {
                                'class_id': class_id,
                                'class_name': Config.FOOD_CLASSES[class_id],
                                'confidence': confidence,
                                'bbox': [x1, y1, x2, y2],
                                'area': (x2 - x1) * (y2 - y1)
                            }
                            detections.append(detection)
                            
        except Exception as e:
            self.logger.error(f"Error en detección: {e}")
        
        return detections
    
    def _add_stats_panel(self, frame: np.ndarray, current_detections: List[Dict]) -> np.ndarray:
        """Añadir panel de estadísticas"""
        # Calcular estadísticas
        stats = calculate_detection_stats(list(self.detections_history))
        
        # Información actual
        info_lines = [
            f"FPS: {self.current_fps:.1f}",
            f"Frame: {self.frame_count}",
            f"Detecciones actuales: {len(current_detections)}"
        ]
        
        # Añadir estadísticas históricas si hay datos
        if stats:
            stats_lines = format_stats_text(stats)
            info_lines.extend(["--- Estadísticas ---"] + stats_lines)
        
        # Añadir panel
        frame = create_info_panel(frame, info_lines, "top-left")
        
        return frame
    
    def _add_controls_info(self, frame: np.ndarray) -> np.ndarray:
        """Añadir información de controles"""
        controls = [
            "Controles:",
            "Q: Salir",
            "S: Screenshot", 
            "P: Pausar/Reanudar",
            "R: Reset estadísticas",
            "T: Toggle estadísticas",
            "C: Cambiar cámara"
        ]
        
        return create_info_panel(frame, controls, "top-right")
    
    def _add_pause_indicator(self, frame: np.ndarray) -> np.ndarray:
        """Añadir indicador de pausa"""
        height, width = frame.shape[:2]
        
        # Overlay semitransparente
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (width, height), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
        
        # Texto de pausa
        pause_text = "PAUSADO - Presiona P para continuar"
        text_size = cv2.getTextSize(pause_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        text_x = (width - text_size[0]) // 2
        text_y = (height + text_size[1]) // 2
        
        cv2.putText(frame, pause_text, (text_x, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        return frame
    
    def _handle_key(self, key: int, frame: np.ndarray) -> bool:
        """Manejar entrada de teclado"""
        if key == ord('q'):
            return False
        elif key == ord('s'):
            self._save_screenshot(frame)
        elif key == ord('p'):
            self.paused = not self.paused
            status = "pausado" if self.paused else "reanudado"
            print(f"⏸️ Demo {status}")
        elif key == ord('r'):
            self._reset_stats()
        elif key == ord('t'):
            self.show_stats = not self.show_stats
            status = "mostradas" if self.show_stats else "ocultas"
            print(f"📊 Estadísticas {status}")
        elif key == ord('c'):
            self._change_camera()
        
        return True
    
    def _save_screenshot(self, frame: np.ndarray):
        """Guardar screenshot"""
        current_detections = list(self.detections_history)[-1] if self.detections_history else []
        filepath = save_detection_image(frame, current_detections, Config.SCREENSHOTS_DIR)
        print(f"📸 Screenshot guardado: {filepath}")
    
    def _reset_stats(self):
        """Resetear estadísticas"""
        self.detections_history.clear()
        self.frame_times.clear()
        self.frame_count = 0
        print("🔄 Estadísticas reseteadas")
    
    def _change_camera(self):
        """Cambiar cámara (funcionalidad futura)"""
        print("📷 Cambio de cámara no implementado en esta versión")
    
    def _print_controls(self):
        """Imprimir controles disponibles"""
        print("\n🎮 Controles disponibles:")
        print("  Q: Salir del programa")
        print("  S: Tomar screenshot con detecciones")
        print("  P: Pausar/reanudar detección")
        print("  R: Resetear estadísticas")
        print("  T: Mostrar/ocultar estadísticas")
        print("  C: Cambiar cámara (próximamente)")
        print("")

def main():
    """Función principal del demo"""
    print("🍎 Detector de Alimentos con YOLO - Demo Avanzado")
    print("=" * 50)
    
    try:
        detector = AdvancedFoodDetector()
        detector.run_demo()
    except Exception as e:
        print(f"❌ Error en el demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
