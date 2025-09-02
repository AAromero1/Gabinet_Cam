import cv2
import numpy as np
from ultralytics import YOLO
import time
import os
from typing import List, Dict, Tuple

class SimpleFoodDetector:
    """
    Versión simplificada del detector de alimentos para pruebas rápidas
    """
    
    def __init__(self):
        self.model = YOLO("yolov8n.pt")  # Descarga automáticamente si no existe
        # Expandir a más objetos relacionados con alimentos
        self.food_classes = {
            # Alimentos principales
            46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli',
            51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake',
            # Bebidas y contenedores
            39: 'bottle', 41: 'cup',
            # Utensilios
            64: 'bowl', 65: 'fork', 66: 'knife', 67: 'spoon'
        }
        
    def run(self):
        """Ejecutar detección simple"""
        cap = cv2.VideoCapture(0)
        
        print("Detector de alimentos y objetos relacionados iniciado!")
        print("Detecta: alimentos, bebidas, botellas, vasos y utensilios")
        print("Presiona 'q' para salir")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Detectar objetos
            results = self.model(frame, verbose=False)
            
            # Procesar detecciones
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        class_id = int(box.cls)
                        confidence = float(box.conf)
                        
                        # Solo mostrar objetos de interés con confianza > 0.4
                        if class_id in self.food_classes and confidence > 0.4:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            
                            # Dibujar detección
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            label = f"{self.food_classes[class_id]}: {confidence:.2f}"
                            cv2.putText(frame, label, (x1, y1-10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            cv2.imshow('Detector de Alimentos', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = SimpleFoodDetector()
    detector.run()
