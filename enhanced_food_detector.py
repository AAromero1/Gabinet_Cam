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

class EnhancedFoodObjectDetector:
    """
    Detector mejorado que incluye alimentos y objetos relacionados como botellas, latas, etc.
    """
    
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.4):
        """
        Inicializar el detector mejorado
        
        Args:
            model_path: Ruta al modelo YOLO
            confidence_threshold: Umbral de confianza (más bajo para detectar más objetos)
        """
        self.confidence_threshold = confidence_threshold
        self.model = None
        
        # Definir todas las clases relevantes del dataset COCO
        self.target_classes = self._get_target_classes()
        
        # Cargar modelo YOLO
        self._load_model(model_path)
        
        # Colores para las categorías
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
    
    def _get_target_classes(self) -> Dict[int, Dict]:
        """
        Definir todas las clases objetivo con categorías
        """
        target_classes = {
            # === ALIMENTOS ===
            46: {'name': 'banana', 'category': 'fruta', 'priority': 'high'},
            47: {'name': 'apple', 'category': 'fruta', 'priority': 'high'}, 
            48: {'name': 'sandwich', 'category': 'comida_preparada', 'priority': 'high'},
            49: {'name': 'orange', 'category': 'fruta', 'priority': 'high'},
            50: {'name': 'broccoli', 'category': 'vegetal', 'priority': 'high'},
            51: {'name': 'carrot', 'category': 'vegetal', 'priority': 'high'},
            52: {'name': 'hot_dog', 'category': 'comida_preparada', 'priority': 'high'},
            53: {'name': 'pizza', 'category': 'comida_preparada', 'priority': 'high'},
            54: {'name': 'donut', 'category': 'postre', 'priority': 'high'},
            55: {'name': 'cake', 'category': 'postre', 'priority': 'high'},
            
            # === BEBIDAS Y CONTENEDORES ===
            39: {'name': 'bottle', 'category': 'bebida_contenedor', 'priority': 'medium'},
            41: {'name': 'cup', 'category': 'bebida_contenedor', 'priority': 'medium'},
            
            # === SNACKS Y PAQUETES ===
            # Note: COCO no tiene clases específicas para bolsas de snacks o cajas de jugo
            # Pero podemos detectar objetos similares
            67: {'name': 'cell_phone', 'category': 'contexto', 'priority': 'low'},  # contexto de snacking
            73: {'name': 'laptop', 'category': 'contexto', 'priority': 'low'},      # contexto de comida en escritorio
            76: {'name': 'keyboard', 'category': 'contexto', 'priority': 'low'},    # contexto de snacking
            84: {'name': 'book', 'category': 'contexto', 'priority': 'low'},        # contexto de snacking mientras estudia
            
            # === OBJETOS DE MESA/COCINA ===
            64: {'name': 'bowl', 'category': 'utensilio', 'priority': 'medium'},
            65: {'name': 'fork', 'category': 'utensilio', 'priority': 'low'},
            66: {'name': 'knife', 'category': 'utensilio', 'priority': 'low'},
            67: {'name': 'spoon', 'category': 'utensilio', 'priority': 'low'},
        }
        
        # Corregir IDs duplicados
        target_classes[64] = {'name': 'bowl', 'category': 'utensilio', 'priority': 'medium'}
        target_classes[65] = {'name': 'fork', 'category': 'utensilio', 'priority': 'low'}
        target_classes[66] = {'name': 'knife', 'category': 'utensilio', 'priority': 'low'}
        target_classes[67] = {'name': 'spoon', 'category': 'utensilio', 'priority': 'low'}
        
        return target_classes
    
    def _generate_colors(self) -> Dict[str, Tuple[int, int, int]]:
        """Generar colores por categoría"""
        category_colors = {
            'fruta': (0, 255, 0),              # Verde
            'vegetal': (0, 255, 0),            # Verde
            'comida_preparada': (0, 0, 255),   # Rojo
            'postre': (255, 0, 255),           # Magenta
            'bebida_contenedor': (255, 0, 0),  # Azul
            'utensilio': (0, 255, 255),        # Amarillo
            'contexto': (128, 128, 128)        # Gris
        }
        return category_colors
    
    def initialize_camera(self, camera_index: int = 0) -> bool:
        """Inicializar la cámara"""
        try:
            self.cap = cv2.VideoCapture(camera_index)
            
            # Configurar propiedades
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            if not self.cap.isOpened():
                logger.error("No se pudo abrir la cámara")
                return False
                
            logger.info("Cámara inicializada correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error al inicializar la cámara: {e}")
            return False
    
    def detect_objects(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Dict]]:
        """
        Detectar objetos relacionados con alimentos
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
                        confidence = float(box.conf)
                        class_id = int(box.cls)
                        
                        # Verificar si es una clase de interés
                        if class_id in self.target_classes:
                            class_info = self.target_classes[class_id]
                            
                            # Ajustar umbral según prioridad
                            threshold = self._get_threshold_by_priority(class_info['priority'])
                            
                            if confidence >= threshold:
                                x1, y1, x2, y2 = map(int, box.xyxy[0])
                                
                                detection_info = {
                                    'class_id': class_id,
                                    'class_name': class_info['name'],
                                    'category': class_info['category'],
                                    'priority': class_info['priority'],
                                    'confidence': confidence,
                                    'bbox': (x1, y1, x2, y2),
                                    'area': (x2 - x1) * (y2 - y1)
                                }
                                detections.append(detection_info)
                                
                                # Dibujar la detección
                                frame = self._draw_detection(frame, detection_info)
            
        except Exception as e:
            logger.error(f"Error en la detección: {e}")
        
        return frame, detections
    
    def _get_threshold_by_priority(self, priority: str) -> float:
        """Obtener umbral de confianza según prioridad"""
        thresholds = {
            'high': 0.4,    # Alimentos principales
            'medium': 0.5,  # Contenedores y utensilios
            'low': 0.6      # Objetos de contexto
        }
        return thresholds.get(priority, self.confidence_threshold)
    
    def _draw_detection(self, frame: np.ndarray, detection: Dict) -> np.ndarray:
        """Dibujar una detección con información de categoría"""
        x1, y1, x2, y2 = detection['bbox']
        class_name = detection['class_name']
        category = detection['category']
        priority = detection['priority']
        confidence = detection['confidence']
        
        # Color según categoría
        color = self.colors.get(category, (255, 255, 255))
        
        # Grosor según prioridad
        thickness = {'high': 3, 'medium': 2, 'low': 1}[priority]
        
        # Dibujar rectángulo
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
        
        # Preparar texto con categoría
        label = f"{class_name} ({category}): {confidence:.2f}"
        
        # Calcular tamaño del texto
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        text_thickness = 1
        (text_width, text_height), _ = cv2.getTextSize(label, font, font_scale, text_thickness)
        
        # Dibujar fondo del texto
        cv2.rectangle(frame, (x1, y1 - text_height - 10), (x1 + text_width, y1), color, -1)
        
        # Dibujar texto
        cv2.putText(frame, label, (x1, y1 - 5), font, font_scale, (255, 255, 255), text_thickness)
        
        return frame
    
    def run_enhanced_detection(self):
        """Ejecutar detección mejorada en tiempo real"""
        if not self.initialize_camera():
            return
        
        logger.info("Iniciando detección mejorada en tiempo real...")
        logger.info("Detectando: alimentos, bebidas, contenedores y objetos relacionados")
        logger.info("Presiona 'q' para salir, 's' para screenshot, 'c' para estadísticas")
        
        fps_counter = 0
        start_time = time.time()
        detection_stats = {'total': 0, 'by_category': {}}
        
        try:
            while True:
                ret, frame = self.cap.read()
                
                if not ret:
                    logger.error("No se pudo leer el frame de la cámara")
                    break
                
                # Detectar objetos
                processed_frame, detections = self.detect_objects(frame)
                
                # Actualizar estadísticas
                self._update_stats(detections, detection_stats)
                
                # Calcular FPS
                fps_counter += 1
                if fps_counter % 30 == 0:
                    end_time = time.time()
                    fps = 30 / (end_time - start_time)
                    start_time = end_time
                    logger.info(f"FPS: {fps:.2f}")
                
                # Añadir información al frame
                self._add_enhanced_info(processed_frame, detections, fps_counter, detection_stats)
                
                # Mostrar frame
                cv2.imshow('Detector Mejorado - Alimentos y Objetos', processed_frame)
                
                # Manejar teclas
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self._save_enhanced_screenshot(processed_frame, detections)
                elif key == ord('c'):
                    self._print_stats(detection_stats)
                    
        except KeyboardInterrupt:
            logger.info("Detección interrumpida por el usuario")
        except Exception as e:
            logger.error(f"Error durante la detección: {e}")
        finally:
            self.cleanup()
    
    def _update_stats(self, detections: List[Dict], stats: Dict):
        """Actualizar estadísticas de detección"""
        stats['total'] += len(detections)
        
        for detection in detections:
            category = detection['category']
            if category not in stats['by_category']:
                stats['by_category'][category] = 0
            stats['by_category'][category] += 1
    
    def _add_enhanced_info(self, frame: np.ndarray, detections: List[Dict], 
                          frame_count: int, stats: Dict):
        """Añadir información mejorada al frame"""
        height, width = frame.shape[:2]
        
        # Contar por categoría
        category_counts = {}
        for detection in detections:
            cat = detection['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # Información actual
        y_offset = 30
        info_lines = [
            f"Frame: {frame_count} | Total detectado: {stats['total']}",
            f"Objetos actuales: {len(detections)}"
        ]
        
        # Añadir conteos por categoría
        if category_counts:
            for category, count in category_counts.items():
                info_lines.append(f"{category}: {count}")
        
        # Dibujar información
        for i, line in enumerate(info_lines):
            y_pos = y_offset + (i * 25)
            cv2.putText(frame, line, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.6, (255, 255, 255), 2)
        
        # Instrucciones
        instructions = "q:salir | s:screenshot | c:estadisticas"
        cv2.putText(frame, instructions, (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.5, (255, 255, 255), 1)
    
    def _save_enhanced_screenshot(self, frame: np.ndarray, detections: List[Dict]):
        """Guardar screenshot con información detallada"""
        timestamp = int(time.time())
        filename = f"enhanced_detection_{timestamp}.jpg"
        
        cv2.imwrite(filename, frame)
        logger.info(f"Screenshot guardado: {filename}")
        
        # Guardar información detallada
        if detections:
            info_filename = f"enhanced_detections_{timestamp}.txt"
            with open(info_filename, 'w') as f:
                f.write(f"=== DETECCIÓN MEJORADA ===\n")
                f.write(f"Archivo: {filename}\n")
                f.write(f"Timestamp: {time.ctime(timestamp)}\n")
                f.write(f"Total objetos: {len(detections)}\n\n")
                
                # Agrupar por categoría
                by_category = {}
                for detection in detections:
                    cat = detection['category']
                    if cat not in by_category:
                        by_category[cat] = []
                    by_category[cat].append(detection)
                
                # Escribir por categoría
                for category, items in by_category.items():
                    f.write(f"=== {category.upper()} ({len(items)} objetos) ===\n")
                    for item in items:
                        f.write(f"- {item['class_name']}: {item['confidence']:.3f} "
                               f"(prioridad: {item['priority']})\n")
                        f.write(f"  Bbox: {item['bbox']}, Área: {item['area']} px²\n")
                    f.write("\n")
            
            logger.info(f"Información detallada guardada: {info_filename}")
    
    def _print_stats(self, stats: Dict):
        """Imprimir estadísticas en consola"""
        print(f"\n=== ESTADÍSTICAS DE DETECCIÓN ===")
        print(f"Total objetos detectados: {stats['total']}")
        print(f"Por categoría:")
        for category, count in stats['by_category'].items():
            print(f"  {category}: {count}")
        print("=" * 35)
    
    def cleanup(self):
        """Limpiar recursos"""
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        logger.info("Recursos liberados")

def main():
    """Función principal del detector mejorado"""
    try:
        print("🍎🥤 Detector Mejorado de Alimentos y Objetos")
        print("Detecta: alimentos, bebidas, contenedores, utensilios y contexto")
        print("=" * 60)
        
        # Crear detector con umbral más bajo para detectar más objetos
        detector = EnhancedFoodObjectDetector(
            model_path="yolov8n.pt",
            confidence_threshold=0.4
        )
        
        # Ejecutar detección
        detector.run_enhanced_detection()
        
    except Exception as e:
        logger.error(f"Error en la aplicación principal: {e}")

if __name__ == "__main__":
    main()
