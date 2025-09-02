import cv2
import numpy as np
import os
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import logging

def setup_logging(level: str = "INFO", format_str: str = None):
    """
    Configurar el sistema de logging
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        format_str: Formato personalizado para los logs
    """
    if format_str is None:
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_str,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('food_detector.log')
        ]
    )

def calculate_fps(frame_times: List[float], window_size: int = 30) -> float:
    """
    Calcular FPS basado en tiempos de frame
    
    Args:
        frame_times: Lista de timestamps de frames
        window_size: Tamaño de la ventana para calcular FPS
        
    Returns:
        float: FPS calculado
    """
    if len(frame_times) < 2:
        return 0.0
    
    recent_times = frame_times[-window_size:]
    if len(recent_times) < 2:
        return 0.0
    
    time_diff = recent_times[-1] - recent_times[0]
    if time_diff == 0:
        return 0.0
    
    return (len(recent_times) - 1) / time_diff

def resize_frame(frame: np.ndarray, max_width: int = 1280, max_height: int = 720) -> np.ndarray:
    """
    Redimensionar frame manteniendo la relación de aspecto
    
    Args:
        frame: Frame a redimensionar
        max_width: Ancho máximo
        max_height: Alto máximo
        
    Returns:
        np.ndarray: Frame redimensionado
    """
    height, width = frame.shape[:2]
    
    # Calcular factor de escala
    scale_width = max_width / width
    scale_height = max_height / height
    scale = min(scale_width, scale_height)
    
    # Solo redimensionar si el frame es más grande
    if scale < 1.0:
        new_width = int(width * scale)
        new_height = int(height * scale)
        frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    return frame

def draw_text_with_background(frame: np.ndarray, text: str, position: Tuple[int, int], 
                            font_scale: float = 0.6, thickness: int = 2, 
                            text_color: Tuple[int, int, int] = (255, 255, 255),
                            bg_color: Tuple[int, int, int] = (0, 0, 0)) -> np.ndarray:
    """
    Dibujar texto con fondo en un frame
    
    Args:
        frame: Frame donde dibujar
        text: Texto a dibujar
        position: Posición (x, y) del texto
        font_scale: Escala de la fuente
        thickness: Grosor del texto
        text_color: Color del texto (BGR)
        bg_color: Color del fondo (BGR)
        
    Returns:
        np.ndarray: Frame con texto dibujado
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    x, y = position
    
    # Calcular tamaño del texto
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    # Dibujar fondo
    cv2.rectangle(frame, (x, y - text_height - baseline), 
                 (x + text_width, y + baseline), bg_color, -1)
    
    # Dibujar texto
    cv2.putText(frame, text, (x, y), font, font_scale, text_color, thickness)
    
    return frame

def create_detection_overlay(frame: np.ndarray, detections: List[Dict], 
                           class_colors: Dict[int, Tuple[int, int, int]]) -> np.ndarray:
    """
    Crear overlay con todas las detecciones
    
    Args:
        frame: Frame base
        detections: Lista de detecciones
        class_colors: Colores por clase
        
    Returns:
        np.ndarray: Frame con overlay
    """
    overlay = frame.copy()
    
    for detection in detections:
        class_id = detection['class_id']
        class_name = detection['class_name']
        confidence = detection['confidence']
        x1, y1, x2, y2 = detection['bbox']
        
        # Color para esta clase
        color = class_colors.get(class_id, (0, 255, 0))
        
        # Dibujar rectángulo
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
        
        # Dibujar etiqueta con fondo
        label = f"{class_name}: {confidence:.2f}"
        overlay = draw_text_with_background(
            overlay, label, (x1, y1 - 5), 
            text_color=(255, 255, 255), bg_color=color
        )
    
    return overlay

def save_detection_image(frame: np.ndarray, detections: List[Dict], 
                        output_dir: str = "screenshots") -> str:
    """
    Guardar imagen con detecciones
    
    Args:
        frame: Frame a guardar
        detections: Lista de detecciones
        output_dir: Directorio de salida
        
    Returns:
        str: Ruta del archivo guardado
    """
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"detection_{timestamp}.jpg"
    filepath = os.path.join(output_dir, filename)
    
    # Guardar imagen
    cv2.imwrite(filepath, frame)
    
    # Guardar información de detecciones
    info_filename = f"detection_{timestamp}.txt"
    info_filepath = os.path.join(output_dir, info_filename)
    
    with open(info_filepath, 'w') as f:
        f.write(f"Detecciones en {filename}:\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Total detecciones: {len(detections)}\n\n")
        
        for i, detection in enumerate(detections, 1):
            f.write(f"{i}. {detection['class_name']}: {detection['confidence']:.3f}\n")
            f.write(f"   Bbox: {detection['bbox']}\n")
            if 'area' in detection:
                f.write(f"   Área: {detection['area']} px²\n")
            f.write("\n")
    
    return filepath

def check_camera_availability(camera_index: int = 0) -> bool:
    """
    Verificar si una cámara está disponible
    
    Args:
        camera_index: Índice de la cámara a verificar
        
    Returns:
        bool: True si la cámara está disponible
    """
    cap = cv2.VideoCapture(camera_index)
    is_available = cap.isOpened()
    cap.release()
    return is_available

def get_available_cameras(max_cameras: int = 10) -> List[int]:
    """
    Obtener lista de cámaras disponibles
    
    Args:
        max_cameras: Número máximo de cámaras a verificar
        
    Returns:
        List[int]: Lista de índices de cámaras disponibles
    """
    available_cameras = []
    
    for i in range(max_cameras):
        if check_camera_availability(i):
            available_cameras.append(i)
    
    return available_cameras

def calculate_detection_stats(detections_history: List[List[Dict]]) -> Dict:
    """
    Calcular estadísticas de detecciones
    
    Args:
        detections_history: Historial de detecciones por frame
        
    Returns:
        Dict: Estadísticas calculadas
    """
    if not detections_history:
        return {}
    
    total_frames = len(detections_history)
    frames_with_detections = sum(1 for dets in detections_history if len(dets) > 0)
    total_detections = sum(len(dets) for dets in detections_history)
    
    # Contar por clase
    class_counts = {}
    confidence_sums = {}
    
    for frame_detections in detections_history:
        for detection in frame_detections:
            class_name = detection['class_name']
            confidence = detection['confidence']
            
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
            confidence_sums[class_name] = confidence_sums.get(class_name, 0) + confidence
    
    # Calcular confianza promedio por clase
    avg_confidence_by_class = {}
    for class_name, total_conf in confidence_sums.items():
        avg_confidence_by_class[class_name] = total_conf / class_counts[class_name]
    
    stats = {
        'total_frames': total_frames,
        'frames_with_detections': frames_with_detections,
        'detection_rate': frames_with_detections / total_frames if total_frames > 0 else 0,
        'total_detections': total_detections,
        'avg_detections_per_frame': total_detections / total_frames if total_frames > 0 else 0,
        'class_counts': class_counts,
        'avg_confidence_by_class': avg_confidence_by_class,
        'most_detected_food': max(class_counts.items(), key=lambda x: x[1])[0] if class_counts else None
    }
    
    return stats

def format_stats_text(stats: Dict) -> List[str]:
    """
    Formatear estadísticas como texto para mostrar en pantalla
    
    Args:
        stats: Diccionario de estadísticas
        
    Returns:
        List[str]: Lista de líneas de texto formateadas
    """
    if not stats:
        return ["No hay estadísticas disponibles"]
    
    lines = [
        f"Frames: {stats['total_frames']}",
        f"Con detecciones: {stats['frames_with_detections']} ({stats['detection_rate']:.1%})",
        f"Total detecciones: {stats['total_detections']}",
        f"Promedio/frame: {stats['avg_detections_per_frame']:.1f}"
    ]
    
    if stats['most_detected_food']:
        lines.append(f"Más detectado: {stats['most_detected_food']}")
    
    return lines

def create_info_panel(frame: np.ndarray, info_lines: List[str], 
                     position: str = "top-left") -> np.ndarray:
    """
    Crear panel de información en el frame
    
    Args:
        frame: Frame donde añadir el panel
        info_lines: Líneas de información a mostrar
        position: Posición del panel ("top-left", "top-right", "bottom-left", "bottom-right")
        
    Returns:
        np.ndarray: Frame con panel de información
    """
    height, width = frame.shape[:2]
    font_scale = 0.5
    thickness = 1
    line_height = 20
    padding = 10
    
    # Calcular posición inicial
    if position == "top-left":
        start_x, start_y = padding, padding + line_height
    elif position == "top-right":
        start_x, start_y = width - 250, padding + line_height
    elif position == "bottom-left":
        start_x, start_y = padding, height - (len(info_lines) * line_height) - padding
    else:  # bottom-right
        start_x, start_y = width - 250, height - (len(info_lines) * line_height) - padding
    
    # Dibujar fondo del panel
    panel_width = 240
    panel_height = len(info_lines) * line_height + padding
    cv2.rectangle(frame, 
                 (start_x - padding, start_y - line_height), 
                 (start_x + panel_width, start_y + panel_height - line_height),
                 (0, 0, 0), -1)
    cv2.rectangle(frame, 
                 (start_x - padding, start_y - line_height), 
                 (start_x + panel_width, start_y + panel_height - line_height),
                 (255, 255, 255), 1)
    
    # Dibujar líneas de información
    for i, line in enumerate(info_lines):
        y_pos = start_y + (i * line_height)
        cv2.putText(frame, line, (start_x, y_pos), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
    
    return frame
