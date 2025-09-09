# 🎬 Detector de Video - Alimentos y Objetos

## 📋 Descripción
Sistema mejorado de detección de objetos usando YOLO que puede procesar videos y cámaras en tiempo real. Detecta alimentos, bebidas, latas, galletas y objetos relacionados con un sistema inteligente de tracking que reduce falsos positivos.

## 🚀 Uso Rápido

### Para Videos
```bash
# Procesar un video específico
python enhanced_food_detector.py --video mi_video.mp4 --output resultado.mp4

# O usar el script simplificado
python video_detector.py mi_video.mp4

# Con configuración personalizada
python video_detector.py mi_video.mp4 resultado.mp4 0.5
```

### Para Cámara en Tiempo Real
```bash
# Usar cámara web
python enhanced_food_detector.py

# O modo simple
python enhanced_food_detector.py
```

### Demostración Completa
```bash
# Ejecutar demo interactivo
python demo_video.py
```

## 📁 Formatos de Video Soportados
- `.mp4` (recomendado)
- `.avi`
- `.mov`
- `.mkv`
- `.webm`

## ⚙️ Parámetros

### Línea de Comandos
- `--video, -v`: Ruta del video de entrada
- `--output, -o`: Ruta del video de salida
- `--confidence, -c`: Umbral de confianza (0.0-1.0, default: 0.4)
- `--model, -m`: Modelo YOLO a usar (default: yolov8n.pt)

### Ejemplos
```bash
# Ejemplo básico
python enhanced_food_detector.py --video cocina.mp4

# Con salida personalizada
python enhanced_food_detector.py -v cocina.mp4 -o cocina_detectado.mp4

# Ajustar sensibilidad
python enhanced_food_detector.py -v cocina.mp4 -c 0.3  # Más sensible
python enhanced_food_detector.py -v cocina.mp4 -c 0.6  # Menos sensible

# Modelo específico
python enhanced_food_detector.py -v cocina.mp4 -m yolov8s.pt
```

## 🎯 Objetos Detectados

### Alimentos (Alta Prioridad)
- 🍌 Frutas: banana, manzana, naranja
- 🥕 Vegetales: brócoli, zanahoria
- 🍕 Comida preparada: sándwich, pizza, hot dog
- 🍩 Snacks y postres: donut, cake, galletas

### Bebidas y Contenedores (Media Prioridad)
- 🍼 Botellas y envases
- ☕ Tazas y vasos
- 🥤 Latas (detección inteligente)

### Utensilios (Baja Prioridad)
- 🍽️ Bowls, tenedores, cuchillos, cucharas

## 🎮 Controles Durante Ejecución

### Cámara en Tiempo Real
- `q`: Salir
- `s`: Tomar screenshot
- `c`: Mostrar estadísticas
- `i`: Estado del inventario
- `r`: Forzar registro de objetos actuales
- `t`: Estadísticas de tracking

### Procesamiento de Video
- `q`: Cancelar procesamiento
- Progreso automático con estadísticas

## 🧠 Sistema de Tracking Inteligente

### Características
- **Reducción de Falsos Positivos**: Requiere múltiples detecciones antes de registrar
- **Control de Cantidad**: Solo registra cuando aumenta el número de objetos
- **Limpieza Automática**: Elimina objetos que desaparecen por 100+ frames
- **Tracking por Regiones**: Agrupa objetos cercanos inteligentemente

### Configuración
- **Frames mínimos para registro**: 30
- **Umbral de desaparición**: 100 frames
- **Tamaño de región**: 100x100 píxeles

## 📊 Integración con Google Sheets

### Funcionalidades
- ✅ Registro automático de inventario
- 🔗 Generación automática de sinónimos
- 📋 Bitácora de cambios
- 🗑️ Eliminación automática de objetos desaparecidos

### Configuración
Coloca tu archivo de credenciales de Google Cloud en el directorio:
- `calm-segment-credentials.json`

## 🎬 Salida de Video

### Información Mostrada
- Cajas de detección con categorías
- Nivel de confianza
- Información de tracking en tiempo real
- Estadísticas por frame
- Progreso de procesamiento

### Formatos de Salida
- **Video**: MP4 con codec H.264
- **Screenshots**: JPG con información detallada
- **Logs**: Archivos de texto con estadísticas

## 🛠️ Troubleshooting

### Errores Comunes
1. **"No se puede abrir el video"**: Verificar formato y ruta
2. **"Modelo no encontrado"**: Descargar yolov8n.pt
3. **"Sin conexión a Sheets"**: Verificar credenciales
4. **"Video muy lento"**: Usar modelo más ligero (yolov8n.pt)

### Optimización
- Para videos largos: usar `yolov8n.pt` (más rápido)
- Para mejor precisión: usar `yolov8m.pt` o `yolov8l.pt`
- Ajustar `confidence` según necesidades

## 📈 Estadísticas de Salida

### Durante Procesamiento
- FPS en tiempo real
- Progreso de video (%)
- Objetos detectados por frame
- Estado de tracking

### Al Finalizar
- Total de frames procesados
- Total de objetos detectados
- Distribución por categorías
- Objetos registrados en inventario
- Ruta del video de salida

## 🎯 Casos de Uso

### Monitoreo de Cocina
```bash
python enhanced_food_detector.py --video cocina_seguridad.mp4 --confidence 0.3
```

### Análisis de Comportamiento Alimentario
```bash
python enhanced_food_detector.py --video comedor.mp4 --output analisis.mp4
```

### Control de Inventario
```bash
python enhanced_food_detector.py --video almacen.mp4 --confidence 0.5
```

## 🔧 Desarrollo y Personalización

### Agregar Nuevas Clases
Modificar `_get_target_classes()` en `enhanced_food_detector.py`

### Ajustar Tracking
Modificar parámetros en `__init__()`:
- `_disappearance_threshold`
- `_min_frames_for_registration`

### Personalizar Colores
Modificar `_generate_colors()` para cambiar esquema de colores

---

## 📞 Soporte
Para problemas o mejoras, revisa los logs generados durante la ejecución.
