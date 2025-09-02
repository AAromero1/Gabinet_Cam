#!/usr/bin/env python3
"""
Detector de alimentos ultra-simple para pruebas básicas
No requiere archivos adicionales - todo en uno
"""

try:
    import cv2
    import numpy as np
    from ultralytics import YOLO
    print("✅ Todas las librerías están disponibles")
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("Ejecuta: pip install opencv-python ultralytics torch")
    exit(1)

def main():
    print("🍎🥤 Detector de Alimentos y Objetos Ultra-Simple")
    print("================================================")
    
    # Clases expandidas: alimentos + objetos relacionados
    FOOD_CLASSES = {
        # Alimentos principales
        46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli',
        51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake',
        # Bebidas y contenedores  
        39: 'bottle', 41: 'cup',
        # Utensilios de cocina
        64: 'bowl', 65: 'fork', 66: 'knife', 67: 'spoon'
    }
    
    # Cargar modelo (se descarga automáticamente la primera vez)
    print("📥 Cargando modelo YOLO...")
    try:
        model = YOLO("yolov8n.pt")
        print("✅ Modelo cargado")
    except Exception as e:
        print(f"❌ Error al cargar modelo: {e}")
        return
    
    # Inicializar cámara
    print("📷 Inicializando cámara...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara")
        print("💡 Verifica que tienes una cámara conectada")
        return
    
    print("✅ Cámara inicializada")
    print("\n🎮 Controles:")
    print("  - Presiona 'q' para salir")
    print("  - Presiona 's' para guardar imagen")
    print("\n🚀 ¡Detector iniciado! Muestra alimentos, bebidas, botellas o utensilios a la cámara...")
    
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("❌ No se pudo leer frame de la cámara")
                break
            
            frame_count += 1
            
            # Detectar solo cada 5 frames para mejor rendimiento
            if frame_count % 5 == 0:
                try:
                    results = model(frame, verbose=False)
                    
                    # Procesar detecciones
                    detections_found = 0
                    for result in results:
                        boxes = result.boxes
                        if boxes is not None:
                            for box in boxes:
                                class_id = int(box.cls)
                                confidence = float(box.conf)
                                
                                # Solo mostrar objetos de interés con confianza > 40%
                                if class_id in FOOD_CLASSES and confidence > 0.4:
                                    detections_found += 1
                                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                                    
                                    # Dibujar rectángulo verde
                                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                    
                                    # Etiqueta con nombre y confianza
                                    label = f"{FOOD_CLASSES[class_id]}: {confidence:.0%}"
                                    
                                    # Fondo para el texto
                                    (text_width, text_height), _ = cv2.getTextSize(
                                        label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                                    )
                                    cv2.rectangle(frame, (x1, y1-text_height-10), 
                                                (x1+text_width, y1), (0, 255, 0), -1)
                                    
                                    # Texto blanco
                                    cv2.putText(frame, label, (x1, y1-5), 
                                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    # Mostrar contador en pantalla
                    if detections_found > 0:
                        counter_text = f"Objetos detectados: {detections_found}"
                        cv2.putText(frame, counter_text, (10, 30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                except Exception as e:
                    print(f"⚠️ Error en detección: {e}")
            
            # Instrucciones en pantalla
            height = frame.shape[0]
            cv2.putText(frame, "Presiona 'q' para salir, 's' para guardar", 
                       (10, height-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Mostrar frame
            cv2.imshow('Detector de Alimentos - Simple', frame)
            
            # Manejar teclas
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"deteccion_{frame_count}.jpg"
                cv2.imwrite(filename, frame)
                print(f"💾 Imagen guardada: {filename}")
    
    except KeyboardInterrupt:
        print("\n⚠️ Interrumpido por el usuario")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Cámara liberada y ventanas cerradas")
        print("👋 ¡Gracias por usar el detector!")

if __name__ == "__main__":
    main()
