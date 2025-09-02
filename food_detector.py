import cv2
import torch
from ultralytics import YOLO
import numpy as np
import time
from typing import List, Dict, Tuple
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FoodDetector:
    """
    Detector de alimentos usando YOLO en tiempo real con webcam
    """
    
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.5):
        """
        Inicializar el detector de alimentos
        
        Args:
            model_path: Ruta al modelo YOLO (por defecto yolov8n.pt)
            confidence_threshold: Umbral de confianza para las detecciones
        """
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.cap = None
        self.food_classes = self._get_food_classes()
        
        # Cargar modelo YOLO
        self._load_model(model_path)
        
        # Colores para las clases (BGR format)
        self.colors = self._generate_colors()
        
    def _load_model(self, model_path: str):
        """Cargar el modelo YOLO"""
        try:
            logger.info(f"Cargando modelo YOLO: {model_path}")
            self.model = YOLO(model_path)
            logger.info("Modelo cargado exitosamente")
        except Exception as e:
            logger.error(f"Error al cargar el modelo: {e}")
            raise
    
    def _get_food_classes(self) -> Dict[int, str]:
        """
        Definir las clases de alimentos y objetos relacionados basadas en COCO dataset
        Retorna un diccionario con ID de clase y nombre
        """
        # Clases expandidas: alimentos + objetos relacionados
        food_classes = {
            # Alimentos principales
            46: 'banana',
            47: 'apple', 
            48: 'sandwich',
            49: 'orange',
            50: 'broccoli',
            51: 'carrot',
            52: 'hot dog',
            53: 'pizza',
            54: 'donut',
            55: 'cake',
            # Bebidas y contenedores
            39: 'bottle',
            41: 'cup',
            # Utensilios
            64: 'bowl', 
            65: 'fork', 
            66: 'knife', 
            67: 'spoon'
        }
        return food_classes
    
    def _generate_colors(self) -> Dict[int, Tuple[int, int, int]]:
        """Generar colores únicos para cada clase"""
        colors = {}
        for class_id in self.food_classes.keys():
            # Generar color basado en el ID de clase
            np.random.seed(class_id)
            color = tuple(map(int, np.random.randint(0, 255, 3)))
            colors[class_id] = color
        return colors
    
    def initialize_camera(self, camera_index: int = 0) -> bool:
        """
        Inicializar la cámara con detección automática de cámaras USB
        
        Args:
            camera_index: Índice de la cámara (0 por defecto)
            
        Returns:
            bool: True si se inicializó correctamente
        """
        logger.info("🔍 Buscando cámaras disponibles...")
        
        # Intentar múltiples índices de cámara (común en sistemas Linux con USB)
        camera_indices_to_try = [0, 1, 2, 3, 4, "/dev/video0", "/dev/video1", "/dev/video2"]
        
        for index in camera_indices_to_try:
            try:
                logger.info(f"Probando cámara en índice: {index}")
                self.cap = cv2.VideoCapture(index)
                
                # Verificar si se abrió correctamente
                if self.cap.isOpened():
                    # Probar leer un frame
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        logger.info(f"✅ Cámara encontrada en índice: {index}")
                        
                        # Configurar propiedades de la cámara
                        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Resolución más baja para compatibilidad
                        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        self.cap.set(cv2.CAP_PROP_FPS, 15)  # FPS más bajo para estabilidad
                        
                        logger.info("📷 Cámara configurada correctamente")
                        return True
                    else:
                        logger.warning(f"Cámara en {index} se abre pero no puede leer frames")
                        self.cap.release()
                else:
                    logger.warning(f"No se pudo abrir cámara en índice: {index}")
                    
            except Exception as e:
                logger.warning(f"Error probando cámara {index}: {e}")
                if hasattr(self, 'cap') and self.cap:
                    self.cap.release()
        
        # Si llegamos aquí, no encontramos ninguna cámara
        logger.error("❌ No se encontró ninguna cámara funcional")
        self._print_camera_troubleshooting()
        return False
    
    def detect_food(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Dict]]:
        """
        Detectar alimentos en un frame
        
        Args:
            frame: Frame de la cámara
            
        Returns:
            Tuple[np.ndarray, List[Dict]]: Frame procesado y lista de detecciones
        """
        detections = []
        
        try:
            # Realizar predicción
            results = self.model(frame, verbose=False)
            
            # Procesar resultados
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Obtener datos de la detección
                        confidence = float(box.conf)
                        class_id = int(box.cls)
                        
                        # Filtrar solo alimentos con confianza suficiente
                        if confidence >= self.confidence_threshold and class_id in self.food_classes:
                            # Coordenadas de la caja
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            
                            # Información de la detección
                            detection_info = {
                                'class_id': class_id,
                                'class_name': self.food_classes[class_id],
                                'confidence': confidence,
                                'bbox': (x1, y1, x2, y2)
                            }
                            detections.append(detection_info)
                            
                            # Dibujar la detección
                            frame = self._draw_detection(frame, detection_info)
            
        except Exception as e:
            logger.error(f"Error en la detección: {e}")
        
        return frame, detections
    
    def _draw_detection(self, frame: np.ndarray, detection: Dict) -> np.ndarray:
        """
        Dibujar una detección en el frame
        
        Args:
            frame: Frame donde dibujar
            detection: Información de la detección
            
        Returns:
            np.ndarray: Frame con la detección dibujada
        """
        x1, y1, x2, y2 = detection['bbox']
        class_name = detection['class_name']
        confidence = detection['confidence']
        class_id = detection['class_id']
        
        # Color para esta clase
        color = self.colors.get(class_id, (0, 255, 0))
        
        # Dibujar rectángulo
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Preparar texto
        label = f"{class_name}: {confidence:.2f}"
        
        # Calcular tamaño del texto
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        (text_width, text_height), _ = cv2.getTextSize(label, font, font_scale, thickness)
        
        # Dibujar fondo del texto
        cv2.rectangle(frame, (x1, y1 - text_height - 10), (x1 + text_width, y1), color, -1)
        
        # Dibujar texto
        cv2.putText(frame, label, (x1, y1 - 5), font, font_scale, (255, 255, 255), thickness)
        
        return frame
    
    def _print_camera_troubleshooting(self):
        """Imprimir información de solución de problemas para cámaras"""
        print("\n" + "="*60)
        print("🔧 SOLUCIÓN DE PROBLEMAS - CÁMARA USB")
        print("="*60)
        print("❌ No se pudo detectar tu cámara USB. Prueba lo siguiente:")
        print("")
        print("1. 🔌 Verificar conexión:")
        print("   • Desconecta y vuelve a conectar la cámara USB")
        print("   • Prueba otro puerto USB")
        print("   • Verifica que la cámara funcione en otras aplicaciones")
        print("")
        print("2. 📱 Verificar permisos:")
        print("   • Ejecuta: sudo chmod 666 /dev/video*")
        print("   • O ejecuta el script como: sudo python3 food_detector.py")
        print("")
        print("3. 🔍 Verificar dispositivos:")
        print("   • Ejecuta: ls /dev/video*")
        print("   • Ejecuta: lsusb | grep -i camera")
        print("")
        print("4. 📦 Instalar drivers:")
        print("   • sudo apt-get update")
        print("   • sudo apt-get install cheese guvcview")
        print("   • Prueba: cheese (para verificar que la cámara funciona)")
        print("")
        print("5. 🐧 Alternativas en Linux:")
        print("   • Algunas cámaras USB necesitan drivers específicos")
        print("   • Verifica la compatibilidad con UVC (USB Video Class)")
        print("")
        print("6. 🔄 Reiniciar servicios:")
        print("   • sudo modprobe -r uvcvideo")
        print("   • sudo modprobe uvcvideo")
        print("="*60)
    
    def run_real_time_detection(self):
        """
        Ejecutar detección en tiempo real
        """
        if not self.initialize_camera():
            return
        
        logger.info("Iniciando detección en tiempo real...")
        logger.info("Presiona 'q' para salir, 's' para tomar screenshot")
        
        fps_counter = 0
        start_time = time.time()
        
        try:
            while True:
                ret, frame = self.cap.read()
                
                if not ret:
                    logger.error("No se pudo leer el frame de la cámara")
                    break
                
                # Detectar alimentos
                processed_frame, detections = self.detect_food(frame)
                
                # Calcular FPS
                fps_counter += 1
                if fps_counter % 30 == 0:
                    end_time = time.time()
                    fps = 30 / (end_time - start_time)
                    start_time = end_time
                    logger.info(f"FPS: {fps:.2f}")
                
                # Añadir información al frame
                self._add_info_to_frame(processed_frame, detections, fps_counter)
                
                # Mostrar frame
                cv2.imshow('Detección de Alimentos - YOLO', processed_frame)
                
                # Manejar teclas
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self._save_screenshot(processed_frame, detections)
                    
        except KeyboardInterrupt:
            logger.info("Detección interrumpida por el usuario")
        except Exception as e:
            logger.error(f"Error durante la detección: {e}")
        finally:
            self.cleanup()
    
    def _add_info_to_frame(self, frame: np.ndarray, detections: List[Dict], frame_count: int):
        """Añadir información general al frame"""
        height, width = frame.shape[:2]
        
        # Información general
        info_text = f"Objetos detectados: {len(detections)} | Frame: {frame_count}"
        cv2.putText(frame, info_text, (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, (255, 255, 255), 2)
        
        # Instrucciones
        instructions = "q:salir | s:screenshot | Detecta: alimentos, bebidas, utensilios"
        cv2.putText(frame, instructions, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.5, (255, 255, 255), 1)
    
    def _save_screenshot(self, frame: np.ndarray, detections: List[Dict]):
        """Guardar screenshot con detecciones"""
        timestamp = int(time.time())
        filename = f"food_detection_{timestamp}.jpg"
        
        cv2.imwrite(filename, frame)
        logger.info(f"Screenshot guardado: {filename}")
        
        # Guardar información de detecciones
        if detections:
            info_filename = f"detections_{timestamp}.txt"
            with open(info_filename, 'w') as f:
                f.write(f"Detecciones en {filename}:\n")
                for i, detection in enumerate(detections, 1):
                    f.write(f"{i}. {detection['class_name']}: {detection['confidence']:.2f}\n")
            logger.info(f"Información de detecciones guardada: {info_filename}")
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        logger.info("Recursos liberados")

def main():
    """Función principal"""
    try:
        # Crear detector
        detector = FoodDetector(
            model_path="yolov8n.pt",  # Usar modelo nano para velocidad
            confidence_threshold=0.5
        )
        
        # Ejecutar detección en tiempo real
        detector.run_real_time_detection()
        
    except Exception as e:
        logger.error(f"Error en la aplicación principal: {e}")

if __name__ == "__main__":
    main()
