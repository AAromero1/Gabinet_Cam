# Configuraciones para el detector de alimentos
import os

class Config:
    """Configuraciones centralizadas para el proyecto"""
    
    # Configuración del modelo
    MODEL_PATH = "yolov8n.pt"  # Opciones: yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
    CONFIDENCE_THRESHOLD = 0.5
    
    # Configuración de la cámara
    CAMERA_INDEX = 0
    CAMERA_WIDTH = 1280
    CAMERA_HEIGHT = 720
    CAMERA_FPS = 30
    
    # Configuración de salida
    OUTPUT_DIR = "food_data"
    SCREENSHOTS_DIR = "screenshots"
    
    # Clases de alimentos y objetos relacionados (ID del COCO dataset)
    FOOD_CLASSES = {
        # Alimentos
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
        39: 'bottle',         # botellas
        41: 'cup',           # vasos/tazas
        # Objetos relacionados con comida
        73: 'laptop',        # usado para identificar áreas de comida
        76: 'keyboard',      # contexto de escritorio/comida
        84: 'book'           # contexto de snacks mientras estudia
    }
    
    # Categorías específicas para mejor organización
    FOOD_CATEGORIES = {
        'alimentos': [46, 47, 48, 49, 50, 51, 52, 53, 54, 55],
        'bebidas_contenedores': [39, 41],
        'contexto_comida': [73, 76, 84]
    }
    
    # Colores para las clases (BGR format)
    CLASS_COLORS = {
        # Alimentos - colores naturales
        46: (0, 255, 255),    # banana - amarillo
        47: (0, 0, 255),      # apple - rojo
        48: (139, 69, 19),    # sandwich - marrón
        49: (0, 165, 255),    # orange - naranja
        50: (0, 255, 0),      # broccoli - verde
        51: (255, 165, 0),    # carrot - naranja carrot
        52: (203, 192, 255),  # hot dog - rosa
        53: (0, 255, 255),    # pizza - amarillo
        54: (255, 192, 203),  # donut - rosa claro
        55: (255, 255, 0),    # cake - cyan
        # Bebidas y contenedores - tonos azules
        39: (255, 0, 0),      # bottle - azul
        41: (255, 100, 0),    # cup - azul claro
        # Contexto - tonos grises/púrpuras
        73: (128, 0, 128),    # laptop - púrpura
        76: (64, 64, 64),     # keyboard - gris oscuro
        84: (128, 128, 0)     # book - verde oliva
    }
    
    # Configuración de logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configuración de datos
    COLLECTION_INTERVAL_FRAMES = 30  # Detectar cada N frames
    MAX_DETECTIONS_PER_FRAME = 10
    
    @classmethod
    def create_directories(cls):
        """Crear directorios necesarios"""
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.SCREENSHOTS_DIR, exist_ok=True)
    
    @classmethod
    def get_model_info(cls):
        """Obtener información sobre el modelo seleccionado"""
        model_info = {
            "yolov8n.pt": {"size": "Nano", "speed": "Muy rápido", "accuracy": "Básica"},
            "yolov8s.pt": {"size": "Small", "speed": "Rápido", "accuracy": "Buena"},
            "yolov8m.pt": {"size": "Medium", "speed": "Medio", "accuracy": "Muy buena"},
            "yolov8l.pt": {"size": "Large", "speed": "Lento", "accuracy": "Excelente"},
            "yolov8x.pt": {"size": "XLarge", "speed": "Muy lento", "accuracy": "Excepcional"}
        }
        return model_info.get(cls.MODEL_PATH, {"size": "Unknown", "speed": "Unknown", "accuracy": "Unknown"})
