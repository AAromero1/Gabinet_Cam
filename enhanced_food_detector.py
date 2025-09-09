import cv2
import torch
from ultralytics import YOLO
import numpy as np
import time
import os
from typing import List, Dict, Tuple
import logging
from google_sheets_integration import GoogleSheetsManager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedFoodObjectDetector:
    """
    Detector mejorado que incluye alimentos y objetos relacionados como botellas, latas, etc.
    """
    
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.4, 
                 video_source=None, output_video_path: str = None):
        """
        Inicializar el detector mejorado
        
        Args:
            model_path: Ruta al modelo YOLO
            confidence_threshold: Umbral de confianza (más bajo para detectar más objetos)
            video_source: Ruta del video de entrada (None para cámara)
            output_video_path: Ruta del video de salida con detecciones
        """
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.video_source = video_source
        self.output_video_path = output_video_path
        self.video_writer = None
        
        # Definir todas las clases relevantes del dataset COCO
        self.target_classes = self._get_target_classes()
        
        # Cargar modelo YOLO
        self._load_model(model_path)
        
        # Colores para las categorías
        self.colors = self._generate_colors()
        
        # Inicializar manager directo de Google Sheets para inventario
        self.sheets_manager = GoogleSheetsManager()
        if self.sheets_manager.is_connected:
            logger.info("📊 Google Sheets Manager conectado para inventario automático")
        else:
            logger.warning("⚠️ Google Sheets Manager no disponible - solo tracking local")
        
        # Contador para evitar registros duplicados
        self._last_detection_time = {}
        self._detection_cooldown = 5.0  # segundos entre detecciones del mismo objeto
        
        # Sistema de tracking inteligente para inventario
        self._tracked_objects = {}  # {object_key: object_info}
        self._frame_counter = 0
        self._disappearance_threshold = 100  # frames para considerar objeto desaparecido
        self._min_frames_for_registration = 30  # frames mínimos para confirmar objeto
        
        logger.info("🎯 Sistema de tracking inteligente inicializado")
        
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
            54: {'name': 'donut', 'category': 'snack', 'priority': 'high'},  # Incluye galletas tipo donut
            55: {'name': 'cake', 'category': 'postre', 'priority': 'high'},  # Puede detectar galletas grandes tipo cake
            
            # === BEBIDAS Y CONTENEDORES ===
            39: {'name': 'bottle', 'category': 'bebida_contenedor', 'priority': 'medium'},  # Botellas
            41: {'name': 'cup', 'category': 'bebida_contenedor', 'priority': 'medium'},     # Tazas/vasos
            # Nota: Las latas no tienen clase específica en COCO, pero pueden detectarse como:
            # - Objetos cilíndricos pequeños (a veces detectados como bottle)
            # - Agregaremos detección inteligente de latas en el post-procesamiento
            
            # === SNACKS Y PAQUETES ===
            # Note: COCO no tiene clases específicas para bolsas de snacks o cajas de jugo
            # Pero podemos detectar objetos similares
            67: {'name': 'cell_phone', 'category': 'contexto', 'priority': 'low'},  
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
            'snack': (255, 100, 0),            # Naranja (para galletas y snacks)
            'postre': (255, 0, 255),           # Magenta
            'bebida_contenedor': (255, 0, 0),  # Azul
            'utensilio': (0, 255, 255),        # Amarillo
            'contexto': (128, 128, 128)        # Gris
        }
        return category_colors
    
    def initialize_video_source(self) -> bool:
        """Inicializar fuente de video (cámara o archivo)"""
        try:
            if self.video_source is None:
                # Usar cámara
                self.cap = cv2.VideoCapture(0)
                logger.info("Usando cámara web como fuente de video")
            else:
                # Usar archivo de video
                self.cap = cv2.VideoCapture(self.video_source)
                logger.info(f"Usando archivo de video: {self.video_source}")
            
            if not self.cap.isOpened():
                logger.error("No se pudo abrir la fuente de video")
                return False
            
            # Obtener propiedades del video
            self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            logger.info(f"Video: {self.frame_width}x{self.frame_height} @ {self.fps} FPS")
            if self.video_source:
                logger.info(f"Total frames: {self.total_frames}")
            
            # Configurar video writer si se especifica salida
            if self.output_video_path:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                self.video_writer = cv2.VideoWriter(
                    self.output_video_path, 
                    fourcc, 
                    self.fps if self.fps > 0 else 30.0, 
                    (self.frame_width, self.frame_height)
                )
                logger.info(f"Video de salida configurado: {self.output_video_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error al inicializar fuente de video: {e}")
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
                                
                                # Mejorar detección de galletas y latas
                                detection_info = self._enhance_food_detection(detection_info)
                                
                                detections.append(detection_info)
                                
                                # Dibujar la detección
                                frame = self._draw_detection(frame, detection_info)
            
            # Actualizar sistema de tracking inteligente
            self._update_tracked_objects(detections)
            
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
    
    def _enhance_food_detection(self, detection: Dict) -> Dict:
        """
        Mejorar la detección de galletas y latas basándose en características del objeto
        """
        # === DETECCIÓN DE GALLETAS ===
        # Si es un donut pequeño, podría ser una galleta
        if detection['class_name'] == 'donut':
            area = detection['area']
            # Si el área es pequeña (menor a 5000 px²), probablemente sea una galleta
            if area < 5000:
                detection['class_name'] = 'galleta (tipo donut)'
                detection['enhanced'] = True
        
        # Si es un cake muy pequeño, podría ser una galleta grande
        elif detection['class_name'] == 'cake':
            area = detection['area']
            # Si el área es pequeña (menor a 8000 px²), podría ser una galleta grande
            if area < 8000:
                detection['class_name'] = 'galleta (tipo cake)'
                detection['enhanced'] = True
        
        # === DETECCIÓN DE LATAS ===
        # Si es una bottle con proporciones de lata (más alta que ancha y área pequeña-mediana)
        elif detection['class_name'] == 'bottle':
            x1, y1, x2, y2 = detection['bbox']
            width = x2 - x1
            height = y2 - y1
            area = detection['area']
            aspect_ratio = height / width if width > 0 else 0
            
            # Características típicas de una lata:
            # - Más alta que ancha (aspect_ratio > 1.2)
            # - Área moderada (entre 2000 y 15000 px²)
            # - No muy delgada ni muy ancha
            if (1.2 < aspect_ratio < 3.0 and 
                2000 < area < 15000 and 
                30 < width < 150):
                detection['class_name'] = 'lata (refresco/bebida)'
                detection['category'] = 'bebida_contenedor'
                detection['enhanced'] = True
        
        return detection
    
    def _generate_object_key(self, detection: Dict) -> str:
        """Generar clave única para un objeto basada en su clase y categoría"""
        class_name = detection['class_name']
        category = detection['category']
        
        # Para objetos del mismo tipo, usar solo el nombre de clase y categoría
        # Esto permitirá agrupar todos los objetos similares bajo una sola entrada
        return f"{category}_{class_name}"
    
    def _update_tracked_objects(self, detections: List[Dict]):
        """Actualizar el sistema de tracking de objetos"""
        self._frame_counter += 1
        current_frame_objects = {}
        
        # Contar objetos por tipo en el frame actual
        for detection in detections:
            if detection['priority'] in ['high', 'medium']:  # Solo productos importantes
                object_key = self._generate_object_key(detection)
                if object_key not in current_frame_objects:
                    current_frame_objects[object_key] = {
                        'detection': detection,
                        'count': 1
                    }
                else:
                    current_frame_objects[object_key]['count'] += 1
        
        # Procesar objetos detectados
        for object_key, frame_data in current_frame_objects.items():
            detection = frame_data['detection']
            current_count = frame_data['count']
            
            if object_key in self._tracked_objects:
                # Objeto ya existe - actualizar información
                obj_info = self._tracked_objects[object_key]
                obj_info['last_seen_frame'] = self._frame_counter
                obj_info['total_detections'] += 1
                obj_info['confidence_sum'] += detection['confidence']
                obj_info['avg_confidence'] = obj_info['confidence_sum'] / obj_info['total_detections']
                
                # Verificar si ha cambiado la cantidad
                if current_count > obj_info['quantity']:
                    # Aumentó la cantidad - registrar nuevas instancias
                    new_instances = current_count - obj_info['quantity']
                    obj_info['quantity'] = current_count
                    self._register_additional_instances(detection, new_instances, obj_info)
                    logger.info(f"📈 Cantidad aumentada: {detection['class_name']} "
                              f"de {obj_info['quantity'] - new_instances} a {obj_info['quantity']}")
                elif current_count < obj_info['quantity']:
                    # Disminuyó la cantidad - actualizar pero no eliminar aún
                    obj_info['quantity'] = current_count
                    logger.info(f"📉 Cantidad disminuida: {detection['class_name']} "
                              f"a {obj_info['quantity']}")
                    
            else:
                # Nuevo objeto - inicializar tracking
                self._tracked_objects[object_key] = {
                    'detection': detection,
                    'first_seen_frame': self._frame_counter,
                    'last_seen_frame': self._frame_counter,
                    'total_detections': 1,
                    'confidence_sum': detection['confidence'],
                    'avg_confidence': detection['confidence'],
                    'quantity': current_count,
                    'registered': False,
                    'item_id': None  # Un solo ID para todo el grupo
                }
                logger.info(f"🆕 Nuevo objeto tracked: {detection['class_name']} "
                          f"(cantidad inicial: {current_count})")
        
        # Verificar objetos que han desaparecido completamente
        self._check_disappeared_objects(set(current_frame_objects.keys()))
        
        # Registrar objetos que han sido confirmados
        self._register_confirmed_objects()
    
    def _register_additional_instances(self, detection: Dict, new_instances: int, obj_info: Dict):
        """Actualizar cantidad de un objeto existente en lugar de crear nuevos registros"""
        if not self.sheets_manager.is_connected:
            return
        
        try:
            item_name = detection['class_name']
            confidence = obj_info['avg_confidence']
            
            # Si ya hay un item_id registrado, actualizar la cantidad
            if obj_info['item_id']:
                logger.info(f"📈 Actualizando cantidad: {item_name} (+{new_instances} unidades)")
                
                # Actualizar en el inventario usando el ID existente
                success = self.sheets_manager.update_item_quantity(
                    item_id=obj_info['item_id'],
                    new_quantity=obj_info['quantity'],
                    additional_info=f"Cantidad actualizada automáticamente - Frame: {self._frame_counter}"
                )
                
                if success:
                    video_info = f" (VIDEO: {os.path.basename(self.video_source)})" if self.video_source else ""
                    logger.info(f"✅ Cantidad actualizada en Excel{video_info}: {item_name} ahora tiene {obj_info['quantity']} unidades (ID: {obj_info['item_id']})")
                else:
                    logger.warning(f"⚠️ No se pudo actualizar cantidad en inventario: {item_name}")
            else:
                # Si no hay ID aún, registrar por primera vez con la cantidad total
                success = self.sheets_manager.log_detection(
                    item_name=item_name,
                    confidence=confidence,
                    quantity=obj_info['quantity'],
                    additional_info=f"Primera detección con cantidad {obj_info['quantity']} - Frame: {self._frame_counter}"
                )
                
                if success:
                    last_item_id = self.sheets_manager.get_last_item_id()
                    if last_item_id:
                        obj_info['item_id'] = last_item_id
                        self._add_automatic_synonyms(item_name, last_item_id, detection['category'])
                        video_info = f" (VIDEO: {os.path.basename(self.video_source)})" if self.video_source else ""
                        logger.info(f"✅ Nuevo objeto registrado en Excel{video_info}: {item_name} con {obj_info['quantity']} unidades (ID: {last_item_id})")
                
        except Exception as e:
            logger.error(f"❌ Error actualizando cantidad: {e}")
    
    def _check_disappeared_objects(self, current_frame_objects: set):
        """Verificar y eliminar objetos que han desaparecido"""
        disappeared_objects = []
        
        for object_key, obj_info in self._tracked_objects.items():
            if object_key not in current_frame_objects:
                frames_missing = self._frame_counter - obj_info['last_seen_frame']
                
                if frames_missing >= self._disappearance_threshold:
                    # Objeto ha desaparecido - eliminar del inventario si estaba registrado
                    if obj_info['registered'] and obj_info['item_id']:
                        self._remove_disappeared_object(obj_info)
                    
                    disappeared_objects.append(object_key)
                    logger.info(f"🗑️ Objeto desaparecido: {obj_info['detection']['class_name']} "
                              f"(ausente por {frames_missing} frames, cantidad: {obj_info['quantity']})")
        
        # Eliminar objetos desaparecidos del tracking
        for object_key in disappeared_objects:
            del self._tracked_objects[object_key]
    
    def _remove_disappeared_object(self, obj_info: Dict):
        """Eliminar un objeto desaparecido del inventario"""
        if not self.sheets_manager.is_connected:
            return
        
        try:
            item_name = obj_info['detection']['class_name']
            item_id = obj_info['item_id']
            
            if item_id:
                # Registrar eliminación en bitácora
                self.sheets_manager.log_removal_to_bitacora(
                    item_id=item_id,
                    item_name=item_name,
                    reason="objeto_desaparecido_de_camara"
                )
                
                # Eliminar del inventario
                self.sheets_manager.remove_item_from_inventory(
                    item_id=item_id,
                    reason="objeto_desaparecido_de_camara"
                )
                
                logger.info(f"🗑️ Objeto eliminado del inventario: {item_name} "
                          f"({obj_info['quantity']} unidades, ID: {item_id})")
            else:
                logger.info(f"🗑️ Objeto desaparecido sin ID registrado: {item_name}")
            
        except Exception as e:
            logger.error(f"❌ Error eliminando objeto desaparecido: {e}")
    
    def _register_confirmed_objects(self):
        """Registrar objetos que han sido confirmados por tiempo suficiente"""
        for object_key, obj_info in self._tracked_objects.items():
            if (not obj_info['registered'] and 
                obj_info['total_detections'] >= self._min_frames_for_registration):
                
                # Objeto confirmado - registrar en inventario
                if self._register_confirmed_object(obj_info):
                    obj_info['registered'] = True
                    video_info = f" (VIDEO: {os.path.basename(self.video_source)})" if self.video_source else ""
                    logger.info(f"✅ Objeto confirmado y registrado en Excel{video_info}: {obj_info['detection']['class_name']} "
                              f"(confianza promedio: {obj_info['avg_confidence']:.3f})")
    
    def _register_confirmed_object(self, obj_info: Dict) -> bool:
        """Registrar un objeto confirmado en el inventario"""
        if not self.sheets_manager.is_connected:
            return False
        
        try:
            detection = obj_info['detection']
            item_name = detection['class_name']
            confidence = obj_info['avg_confidence']
            quantity = obj_info['quantity']
            
            additional_info = (f"Objeto confirmado después de {obj_info['total_detections']} detecciones. "
                             f"Frames: {obj_info['first_seen_frame']}-{obj_info['last_seen_frame']}. "
                             f"Cantidad: {quantity}")
            
            success = self.sheets_manager.log_detection(
                item_name=item_name,
                confidence=confidence,
                quantity=quantity,
                additional_info=additional_info
            )
            
            if success:
                last_item_id = self.sheets_manager.get_last_item_id()
                if last_item_id:
                    obj_info['item_id'] = last_item_id
                    self._add_automatic_synonyms(item_name, last_item_id, detection['category'])
                    video_info = f" (VIDEO: {os.path.basename(self.video_source)})" if self.video_source else ""
                    logger.info(f"📦 Item registrado exitosamente en Excel{video_info}: {item_name} (ID: {last_item_id})")
                    return True
            
        except Exception as e:
            logger.error(f"❌ Error registrando objeto confirmado: {e}")
        
        return False
    
    def _process_detection_for_inventory(self, detection: Dict) -> bool:
        """
        Procesar una detección y registrarla en el inventario automáticamente
        """
        if not self.sheets_manager.is_connected:
            return False
        
        try:
            # Determinar si es un producto importante para el inventario
            priority = detection.get('priority', 'low')
            category = detection.get('category', 'general')
            
            # Solo registrar productos de alta y media prioridad en inventario
            if priority in ['high', 'medium']:
                item_name = detection['class_name']
                confidence = detection['confidence']
                
                # Información adicional para el inventario
                bbox = detection['bbox']
                area = detection['area']
                additional_info = f"Detectado por cámara - bbox:{bbox}, área:{area}px²"
                
                # Registrar en inventario
                success = self.sheets_manager.log_detection(
                    item_name=item_name,
                    confidence=confidence,
                    additional_info=additional_info
                )
                
                if success:
                    # Obtener el ID del último item registrado
                    last_item_id = self.sheets_manager.get_last_item_id()
                    
                    if last_item_id:
                        # Agregar sinónimos automáticamente
                        self._add_automatic_synonyms(item_name, last_item_id, category)
                        
                        logger.info(f"✅ Producto registrado en inventario: {item_name} (ID: {last_item_id})")
                        return True
                else:
                    logger.warning(f"⚠️ No se pudo registrar en inventario: {item_name}")
            
        except Exception as e:
            logger.error(f"❌ Error procesando detección para inventario: {e}")
        
        return False
    
    def _add_automatic_synonyms(self, item_name: str, item_id: str, category: str):
        """
        Agregar sinónimos automáticamente para un producto detectado
        """
        try:
            synonyms_to_add = []
            item_lower = item_name.lower()
            
            # Generar sinónimos basados en el tipo de producto
            if 'galleta' in item_lower or 'donut' in item_lower or 'cake' in item_lower:
                synonyms_to_add.extend([
                    ('galleta', item_id, 'Snacks'),
                    ('cookie', item_id, 'Snacks'),
                    ('dulce', item_id, 'Snacks')
                ])
                if 'chocolate' in item_lower:
                    synonyms_to_add.append(('chocolate', item_id, 'Snacks'))
            
            elif 'lata' in item_lower or 'bottle' in item_lower:
                synonyms_to_add.extend([
                    ('Jugo', item_id, 'Bebidas'),
                    ('lata', item_id, 'Bebidas'),
                    ('refresco', item_id, 'Bebidas')
                ])
                if 'coca' in item_lower:
                    synonyms_to_add.extend([
                        ('coca', item_id, 'Bebidas'),
                        ('cocacola', item_id, 'Bebidas')
                    ])
            
            elif any(word in item_lower for word in ['banana', 'apple', 'orange']):
                synonyms_to_add.extend([
                    ('fruta', item_id, 'Frutas'),
                    (item_name.split('_')[0], item_id, 'Frutas')  # nombre base
                ])
            
            elif any(word in item_lower for word in ['sandwich', 'pizza', 'hot_dog']):
                synonyms_to_add.extend([
                    ('comida', item_id, 'Alimentos'),
                    ('alimento', item_id, 'Alimentos')
                ])
            
            # Siempre agregar el nombre base como sinónimo
            base_name = item_name.replace('_', ' ').replace('(', '').replace(')', '').strip()
            synonyms_to_add.append((base_name, item_id, category))
            
            # Agregar sinónimos al spreadsheet
            for synonym, syn_item_id, syn_category in synonyms_to_add:
                self.sheets_manager.add_synonym(synonym, syn_item_id, syn_category)
                time.sleep(0.2)  # Pausa para evitar rate limiting
            
        except Exception as e:
            logger.error(f"❌ Error agregando sinónimos automáticos: {e}")
    
    def _draw_detection(self, frame: np.ndarray, detection: Dict) -> np.ndarray:
        """Dibujar una detección con información de categoría"""
        x1, y1, x2, y2 = detection['bbox']
        class_name = detection['class_name']
        category = detection['category']
        priority = detection['priority']
        confidence = detection['confidence']
        
        # Color según categoría
        color = self.colors.get(category, (255, 255, 255))
        
        # Si es una detección mejorada de galleta, usar color especial
        if detection.get('enhanced', False):
            color = (0, 165, 255)  # Naranja brillante para galletas detectadas
        
        # Grosor según prioridad
        thickness = {'high': 3, 'medium': 2, 'low': 1}[priority]
        
        # Dibujar rectángulo
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
        
        # Preparar texto con categoría
        label = f"{class_name} ({category}): {confidence:.2f}"
        if detection.get('enhanced', False):
            if 'galleta' in class_name:
                label = f"🍪 {label} [GALLETA]"
            elif 'lata' in class_name:
                label = f"🥤 {label} [LATA]"
            else:
                label = f"✨ {label} [MEJORADO]"
        
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
    
    def _draw_tracking_info(self, frame: np.ndarray) -> np.ndarray:
        """Dibujar información del sistema de tracking en el frame"""
        try:
            # Información general del tracking
            tracking_info = [
                f"Frame: {self._frame_counter}",
                f"Objetos tracked: {len(self._tracked_objects)}",
                f"Umbral desaparicion: {self._disappearance_threshold} frames"
            ]
            
            y_offset = 30
            for info in tracking_info:
                cv2.putText(frame, info, (10, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                y_offset += 20
            
            # Información detallada de objetos tracked
            if self._tracked_objects:
                y_offset += 10
                cv2.putText(frame, "=== OBJETOS TRACKED ===", (10, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                y_offset += 20
                
                for i, (object_key, obj_info) in enumerate(self._tracked_objects.items()):
                    if i >= 5:  # Máximo 5 objetos para no saturar pantalla
                        cv2.putText(frame, f"... y {len(self._tracked_objects) - 5} más", 
                                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (128, 128, 128), 1)
                        break
                    
                    item_name = obj_info['detection']['class_name']
                    frames_active = self._frame_counter - obj_info['first_seen_frame']
                    frames_since_seen = self._frame_counter - obj_info['last_seen_frame']
                    status = "✅ REG" if obj_info['registered'] else "⏳ PEND"
                    
                    info_text = f"{status} {item_name} x{obj_info['quantity']} (activo:{frames_active}f, último:{frames_since_seen}f)"
                    cv2.putText(frame, info_text, (10, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                    y_offset += 15
            
        except Exception as e:
            logger.error(f"Error dibujando info de tracking: {e}")
        
        return frame
    
    def run_enhanced_detection(self):
        """Ejecutar detección mejorada en tiempo real o en video"""
        if not self.initialize_video_source():
            return
        
        source_type = "video" if self.video_source else "cámara"
        logger.info(f"Iniciando detección mejorada en {source_type}...")
        logger.info("Detectando: alimentos, bebidas, latas, contenedores, galletas y objetos relacionados")
        logger.info("🎯 Sistema de tracking inteligente: reduce falsos positivos")
        logger.info("📦 Inventario automático: registrando productos importantes")
        
        # Verificar estado de Google Sheets para videos
        if self.video_source:
            sheets_status = "✅ ACTIVO" if self.sheets_manager.is_connected else "❌ DESCONECTADO"
            logger.info(f"📊 Google Sheets para videos: {sheets_status}")
            if self.sheets_manager.is_connected:
                logger.info("🎬 Los elementos detectados en el video SÍ se agregarán al Excel/Google Sheets")
            else:
                logger.warning("⚠️ Los elementos detectados en el video NO se agregarán al Excel (falta conexión)")
        else:
            sheets_status = "✅ ACTIVO" if self.sheets_manager.is_connected else "❌ DESCONECTADO"
            logger.info(f"📊 Google Sheets para cámara: {sheets_status}")
        
        if self.video_source:
            logger.info(f"Procesando video: {self.video_source}")
            logger.info(f"Total frames a procesar: {self.total_frames}")
            if self.output_video_path:
                logger.info(f"Guardando resultado en: {self.output_video_path}")
        else:
            logger.info("Presiona 'q' para salir, 's' para screenshot, 'c' para estadísticas")
            logger.info("Presiona 'i' para estado inventario, 'r' para forzar registro, 't' para tracking")
        
        fps_counter = 0
        start_time = time.time()
        detection_stats = {'total': 0, 'by_category': {}}
        processed_frames = 0
        
        try:
            while True:
                ret, frame = self.cap.read()
                
                if not ret:
                    if self.video_source:
                        logger.info("Procesamiento de video completado")
                    else:
                        logger.error("No se pudo leer el frame de la cámara")
                    break
                
                processed_frames += 1
                
                # Detectar objetos
                processed_frame, detections = self.detect_objects(frame)
                
                # Actualizar estadísticas
                self._update_stats(detections, detection_stats)
                
                # Calcular FPS y progreso
                fps_counter += 1
                if fps_counter % 30 == 0:
                    end_time = time.time()
                    fps = 30 / (end_time - start_time)
                    start_time = end_time
                    
                    if self.video_source:
                        progress = (processed_frames / self.total_frames) * 100
                        logger.info(f"Progreso: {processed_frames}/{self.total_frames} ({progress:.1f}%) - FPS: {fps:.2f}")
                    else:
                        logger.info(f"FPS: {fps:.2f}")
                
                # Añadir información al frame
                self._add_enhanced_info(processed_frame, detections, fps_counter, detection_stats)
                
                # Añadir información de tracking
                processed_frame = self._draw_tracking_info(processed_frame)
                
                # Añadir información de progreso para videos
                if self.video_source:
                    progress = (processed_frames / self.total_frames) * 100
                    progress_text = f"Progreso: {processed_frames}/{self.total_frames} ({progress:.1f}%)"
                    cv2.putText(processed_frame, progress_text, (10, self.frame_height - 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Guardar frame en video de salida si está configurado
                if self.video_writer:
                    self.video_writer.write(processed_frame)
                
                # Mostrar frame (opcional para videos)
                if not self.video_source or self.video_source and processed_frames % 5 == 0:  # Mostrar cada 5 frames para videos
                    cv2.imshow('Detector Mejorado - Alimentos y Objetos', processed_frame)
                
                # Manejar teclas (solo para cámara o video con visualización)
                if not self.video_source:
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('s'):
                        self._save_enhanced_screenshot(processed_frame, detections)
                    elif key == ord('c'):
                        self._print_stats(detection_stats)
                    elif key == ord('i'):
                        self._print_inventory_status()
                    elif key == ord('r'):
                        self._force_register_current_detections(detections)
                    elif key == ord('t'):
                        self._print_tracking_stats()
                else:
                    # Para videos, verificar si se presiona 'q' para cancelar
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        logger.info("Procesamiento cancelado por el usuario")
                        break
                    
        except KeyboardInterrupt:
            logger.info("Detección interrumpida por el usuario")
        except Exception as e:
            logger.error(f"Error durante la detección: {e}")
        finally:
            # Mostrar estadísticas finales
            self._print_final_stats(detection_stats, processed_frames)
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
        
        # Información de Google Sheets
        if self.sheets_manager.is_connected:
            info_lines.extend([
                f"--- Google Sheets ---",
                f"Inventario: ✅ Conectado",
                f"Registro automático: Activo"
            ])
        else:
            info_lines.append("Inventario: ❌ Desconectado")
        
        # Añadir conteos por categoría
        if category_counts:
            info_lines.append("--- Categorías ---")
            for category, count in category_counts.items():
                info_lines.append(f"{category}: {count}")
        
        # Dibujar información
        for i, line in enumerate(info_lines):
            y_pos = y_offset + (i * 25)
            cv2.putText(frame, line, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.6, (255, 255, 255), 2)
        
        # Instrucciones actualizadas
        instructions = "q:salir | s:screenshot | c:estadisticas | i:inventario | r:registrar | t:tracking"
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
    
    def _print_inventory_status(self):
        """Imprimir estado del inventario"""
        print(f"\n=== ESTADO DEL INVENTARIO ===")
        print(f"Conexión Sheets: {'✅ Conectado' if self.sheets_manager.is_connected else '❌ Desconectado'}")
        
        if self.sheets_manager.is_connected:
            try:
                # Obtener información del spreadsheet
                info = self.sheets_manager.get_spreadsheet_info()
                print(f"Spreadsheet: {info.get('title', 'N/A')}")
                print(f"Hoja principal: {info.get('worksheet_title', 'N/A')}")
                print(f"Total registros: {info.get('data_rows', 0)}")
                
                # Leer últimos 3 registros
                recent_data = self.sheets_manager.read_existing_data()
                if recent_data:
                    print(f"\n--- ÚLTIMOS REGISTROS ---")
                    for item in recent_data[-3:]:
                        name = item.get('name', 'N/A')
                        item_id = item.get('item_id', 'N/A')
                        category = item.get('category', 'N/A')
                        created = item.get('created_at', 'N/A')
                        print(f"  • {name} (ID: {item_id[:12]}...) - {category}")
                
                # Mostrar estructura de hojas
                print(f"\n--- ESTRUCTURA DETECTADA ---")
                for sheet_name, sheet_info in self.sheets_manager.sheet_structure.items():
                    print(f"  📄 {sheet_name}: {sheet_info['data_rows']} registros")
                
                print(f"\n📊 URL: {self.sheets_manager.get_spreadsheet_url()}")
                
            except Exception as e:
                print(f"❌ Error obteniendo información del inventario: {e}")
        
        print("=" * 32)
    
    def _force_register_current_detections(self, detections: List[Dict]):
        """Forzar registro de las detecciones actuales en el inventario"""
        if not self.sheets_manager.is_connected:
            print("❌ Google Sheets no conectado - no se puede registrar")
            return
        
        if not detections:
            print("ℹ️ No hay detecciones actuales para registrar")
            return
        
        print(f"\n🔥 REGISTRO FORZADO - {len(detections)} detecciones")
        print("-" * 50)
        
        registered_count = 0
        for detection in detections:
            try:
                item_name = detection['class_name']
                confidence = detection['confidence']
                category = detection['category']
                
                print(f"📦 Registrando: {item_name} ({category}) - {confidence:.3f}")
                
                # Registrar en inventario
                success = self.sheets_manager.log_detection(
                    item_name=item_name,
                    confidence=confidence,
                    additional_info=f"Registro manual forzado - {time.ctime()}"
                )
                
                if success:
                    registered_count += 1
                    # Obtener ID y agregar sinónimos
                    last_item_id = self.sheets_manager.get_last_item_id()
                    if last_item_id:
                        self._add_automatic_synonyms(item_name, last_item_id, category)
                        print(f"  ✅ Registrado con ID: {last_item_id}")
                else:
                    print(f"  ❌ Error en registro")
                
                time.sleep(0.5)  # Pausa entre registros
                
            except Exception as e:
                print(f"  ❌ Error registrando {detection.get('class_name', 'unknown')}: {e}")
        
        print(f"\n✅ Registro completado: {registered_count}/{len(detections)} productos")
        print("-" * 50)
    
    def _print_tracking_stats(self):
        """Imprimir estadísticas detalladas del sistema de tracking"""
        print("=" * 60)
        print("📊 ESTADÍSTICAS DEL SISTEMA DE TRACKING")
        print("=" * 60)
        print(f"Frame actual: {self._frame_counter}")
        print(f"Objetos siendo tracked: {len(self._tracked_objects)}")
        print(f"Umbral de desaparición: {self._disappearance_threshold} frames")
        print(f"Frames mínimos para registro: {self._min_frames_for_registration}")
        
        if self._tracked_objects:
            print("\n🎯 OBJETOS TRACKED:")
            for object_key, obj_info in self._tracked_objects.items():
                detection = obj_info['detection']
                frames_active = self._frame_counter - obj_info['first_seen_frame']
                frames_since_seen = self._frame_counter - obj_info['last_seen_frame']
                status = "✅ REGISTRADO" if obj_info['registered'] else "⏳ PENDIENTE"
                
                print(f"  • {detection['class_name']} ({detection['category']})")
                print(f"    - Estado: {status}")
                print(f"    - Cantidad: {obj_info['quantity']}")
                print(f"    - Frames activo: {frames_active}")
                print(f"    - Último visto: hace {frames_since_seen} frames")
                print(f"    - Detecciones totales: {obj_info['total_detections']}")
                print(f"    - Confianza promedio: {obj_info['avg_confidence']:.3f}")
                if obj_info['item_id']:
                    print(f"    - ID en inventario: {obj_info['item_id']}")
                print("")
        else:
            print("🚫 No hay objetos siendo tracked actualmente")
        
        print("=" * 60)
    
    def _print_final_stats(self, stats: Dict, total_frames: int):
        """Imprimir estadísticas finales del procesamiento"""
        logger.info("=" * 60)
        logger.info("📊 ESTADÍSTICAS FINALES")
        logger.info("=" * 60)
        logger.info(f"Frames procesados: {total_frames}")
        logger.info(f"Total objetos detectados: {stats['total']}")
        logger.info(f"Promedio detecciones por frame: {stats['total']/total_frames:.2f}" if total_frames > 0 else "N/A")
        
        if stats['by_category']:
            logger.info("\n📋 Por categoría:")
            for category, count in stats['by_category'].items():
                percentage = (count / stats['total']) * 100 if stats['total'] > 0 else 0
                logger.info(f"  • {category}: {count} ({percentage:.1f}%)")
        
        logger.info(f"\n🎯 Objetos tracked finales: {len(self._tracked_objects)}")
        registered_objects = sum(1 for obj in self._tracked_objects.values() if obj['registered'])
        logger.info(f"📦 Objetos registrados en inventario: {registered_objects}")
        
        if self.output_video_path:
            logger.info(f"\n🎬 Video guardado: {self.output_video_path}")
        
        logger.info("=" * 60)
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        logger.info("Recursos liberados correctamente")
    
    def cleanup(self):
        """Limpiar recursos"""
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()
        if hasattr(self, 'video_writer') and self.video_writer:
            self.video_writer.release()
            logger.info("Video de salida guardado correctamente")
        cv2.destroyAllWindows()
        logger.info("Recursos liberados")

def main():
    """Función principal del detector mejorado"""
    import argparse
    
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Detector Mejorado de Alimentos y Objetos')
    parser.add_argument('--video', '-v', type=str, help='Ruta del video de entrada')
    parser.add_argument('--output', '-o', type=str, help='Ruta del video de salida con detecciones')
    parser.add_argument('--confidence', '-c', type=float, default=0.4, help='Umbral de confianza (default: 0.4)')
    parser.add_argument('--model', '-m', type=str, default='yolov8n.pt', help='Ruta del modelo YOLO (default: yolov8n.pt)')
    
    args = parser.parse_args()
    
    try:
        print("🍎🥤🍪 Detector Mejorado de Alimentos y Objetos con Inventario Automático")
        print("Detecta: alimentos, bebidas, latas, galletas, contenedores, utensilios y contexto")
        print("📦 Inventario automático: registra productos importantes en Google Sheets")
        print("🔗 Sinónimos automáticos: crea términos de búsqueda para cada producto")
        print("🎯 Sistema de tracking inteligente: reduce falsos positivos")
        print("=" * 80)
        
        # Determinar nombres de archivo automáticamente si no se especifican
        if args.video and not args.output:
            import os
            video_name = os.path.splitext(os.path.basename(args.video))[0]
            args.output = f"{video_name}_detected.mp4"
            print(f"📁 Video de salida automático: {args.output}")
        
        # Crear detector
        detector = EnhancedFoodObjectDetector(
            model_path=args.model,
            confidence_threshold=args.confidence,
            video_source=args.video,
            output_video_path=args.output
        )
        
        # Mostrar configuración
        if args.video:
            print(f"📹 Procesando video: {args.video}")
            if args.output:
                print(f"💾 Guardando resultado en: {args.output}")
        else:
            print("📸 Usando cámara web en tiempo real")
        
        print(f"🤖 Modelo: {args.model}")
        print(f"🎯 Umbral de confianza: {args.confidence}")
        print("=" * 80)
        
        # Ejecutar detección
        detector.run_enhanced_detection()
        
    except Exception as e:
        logger.error(f"Error en la aplicación principal: {e}")

def main_simple():
    """Función principal simple para compatibilidad"""
    try:
        print("🍎🥤🍪 Detector Mejorado de Alimentos y Objetos (Modo Simple)")
        print("Usando configuración por defecto...")
        
        # Crear detector con configuración por defecto
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
