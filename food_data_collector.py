import cv2
import numpy as np
from ultralytics import YOLO
import json
import os
from datetime import datetime
from typing import List, Dict

class FoodDataCollector:
    """
    Clase para recopilar datos de alimentos detectados para análisis
    """
    
    def __init__(self, output_dir: str = "food_data"):
        self.model = YOLO("yolov11n.pt")
        self.output_dir = output_dir
        self.food_classes = {
            46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli',
            51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake'
        }
        
        # Crear directorio de salida
        os.makedirs(output_dir, exist_ok=True)
        
        # Archivo para almacenar datos
        self.data_file = os.path.join(output_dir, "food_detections.json")
        self.detections_data = []
        
    def collect_food_data(self, duration_minutes: int = 5):
        """
        Recopilar datos de alimentos durante un tiempo específico
        
        Args:
            duration_minutes: Duración en minutos para recopilar datos
        """
        cap = cv2.VideoCapture(0)
        
        start_time = datetime.now()
        end_time = start_time.timestamp() + (duration_minutes * 60)
        
        print(f"Recopilando datos de alimentos por {duration_minutes} minutos...")
        print("Presiona 'q' para terminar antes")
        
        frame_count = 0
        
        while datetime.now().timestamp() < end_time:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            current_time = datetime.now()
            
            # Detectar cada 30 frames (aprox. 1 vez por segundo)
            if frame_count % 30 == 0:
                detections = self._detect_foods_in_frame(frame)
                
                if detections:
                    # Guardar datos
                    data_entry = {
                        'timestamp': current_time.isoformat(),
                        'frame_number': frame_count,
                        'detections': detections
                    }
                    self.detections_data.append(data_entry)
                    
                    print(f"Frame {frame_count}: {len(detections)} alimentos detectados")
            
            # Mostrar frame con detecciones
            display_frame = self._draw_detections(frame.copy())
            cv2.imshow('Recopilación de Datos - Alimentos', display_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Guardar datos recopilados
        self._save_collected_data()
        self._generate_report()
        
    def _detect_foods_in_frame(self, frame: np.ndarray) -> List[Dict]:
        """Detectar alimentos en un frame específico"""
        detections = []
        
        results = self.model(frame, verbose=False)
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    class_id = int(box.cls)
                    confidence = float(box.conf)
                    
                    if class_id in self.food_classes and confidence > 0.5:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        detection = {
                            'class_id': class_id,
                            'class_name': self.food_classes[class_id],
                            'confidence': round(confidence, 3),
                            'bbox': [x1, y1, x2, y2],
                            'area': (x2 - x1) * (y2 - y1)
                        }
                        detections.append(detection)
        
        return detections
    
    def _draw_detections(self, frame: np.ndarray) -> np.ndarray:
        """Dibujar detecciones en el frame"""
        results = self.model(frame, verbose=False)
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    class_id = int(box.cls)
                    confidence = float(box.conf)
                    
                    if class_id in self.food_classes and confidence > 0.5:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        # Dibujar rectángulo
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        
                        # Etiqueta
                        label = f"{self.food_classes[class_id]}: {confidence:.2f}"
                        cv2.putText(frame, label, (x1, y1-10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame
    
    def _save_collected_data(self):
        """Guardar datos recopilados en JSON"""
        with open(self.data_file, 'w') as f:
            json.dump(self.detections_data, f, indent=2)
        
        print(f"Datos guardados en: {self.data_file}")
    
    def _generate_report(self):
        """Generar reporte de los datos recopilados"""
        if not self.detections_data:
            print("No hay datos para generar reporte")
            return
        
        # Estadísticas
        total_detections = sum(len(entry['detections']) for entry in self.detections_data)
        food_counts = {}
        
        for entry in self.detections_data:
            for detection in entry['detections']:
                food_name = detection['class_name']
                food_counts[food_name] = food_counts.get(food_name, 0) + 1
        
        # Crear reporte
        report = {
            'summary': {
                'total_frames_with_detections': len(self.detections_data),
                'total_food_detections': total_detections,
                'unique_foods_detected': len(food_counts),
                'average_detections_per_frame': round(total_detections / len(self.detections_data), 2) if self.detections_data else 0
            },
            'food_frequency': food_counts,
            'generation_time': datetime.now().isoformat()
        }
        
        # Guardar reporte
        report_file = os.path.join(self.output_dir, "detection_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n--- REPORTE DE DETECCIÓN DE ALIMENTOS ---")
        print(f"Frames con detecciones: {report['summary']['total_frames_with_detections']}")
        print(f"Total de alimentos detectados: {report['summary']['total_food_detections']}")
        print(f"Tipos de alimentos únicos: {report['summary']['unique_foods_detected']}")
        print(f"Promedio por frame: {report['summary']['average_detections_per_frame']}")
        print(f"\nFrecuencia de alimentos:")
        for food, count in sorted(food_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {food}: {count} veces")
        print(f"\nReporte completo guardado en: {report_file}")

def main():
    """Función principal para recopilar datos"""
    collector = FoodDataCollector()
    
    try:
        duration = int(input("¿Por cuántos minutos quieres recopilar datos? (default: 2): ") or "2")
        collector.collect_food_data(duration)
    except ValueError:
        print("Usando duración por defecto de 2 minutos")
        collector.collect_food_data(2)
    except KeyboardInterrupt:
        print("\nRecopilación interrumpida por el usuario")

if __name__ == "__main__":
    main()
