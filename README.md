# Detector de Alimentos y Objetos con YOLO en Tiempo Real 🍎��️

Este proyecto implementa un sistema de detección de alimentos y objetos relacionados en tiempo real usando YOLO (You Only Look Once) y OpenCV con una webcam.

## 🚀 Características

- **Detección en tiempo real**: Usa la webcam para detectar alimentos y objetos instantáneamente
- **Múltiples categorías**: Detecta alimentos, bebidas, contenedores, utensilios y objetos de contexto
- **Interfaz visual**: Muestra cajas delimitadoras con nombres, categorías y confianza
- **Detección inteligente**: Diferentes umbrales de confianza según la importancia del objeto
- **Recopilación de datos**: Guarda automáticamente detecciones y estadísticas por categoría
- **Screenshots mejorados**: Captura imágenes con información detallada de categorías
- **Múltiples versiones**: Desde simple hasta avanzado con estadísticas completas

## 🍎🥤 Objetos Detectados

El sistema puede detectar los siguientes objetos del dataset COCO organizados por categorías:

### 🍎 Alimentos Principales
- 🍌 Banana
- 🍎 Manzana  
- 🥪 Sandwich
- 🍊 Naranja
- 🥦 Brócoli
- 🥕 Zanahoria
- 🌭 Hot dog
- 🍕 Pizza
- 🍩 Dona
- 🎂 Pastel

### 🥤 Bebidas y Contenedores
- 🍶 Botellas (bottle)
- ☕ Vasos/Tazas (cup)

### 🍽️ Utensilios de Cocina
- 🥣 Bowls/Cuencos
- 🍴 Tenedores
- 🔪 Cuchillos  
- 🥄 Cucharas

### 📱 Objetos de Contexto (opcional)
- 💻 Laptop (contexto de snacking en escritorio)
- ⌨️ Teclado (contexto de comida mientras trabajas)
- 📖 Libros (contexto de snacking mientras estudias)

## 📋 Requisitos

### Hardware
- Cámara web funcional
- GPU recomendada (pero no requerida)

### Software
- Python 3.8+
- Ubuntu/Linux (probado en Ubuntu)
- Cámara accesible

## 🛠️ Instalación

### Instalación Automática (Recomendada)

```bash
# Hacer ejecutable el script de instalación
chmod +x install.sh

# Ejecutar instalación
./install.sh
```

### Instalación Manual

```bash
# Crear entorno virtual
python3 -m venv food_detection_env
source food_detection_env/bin/activate

# Instalar dependencias del sistema
sudo apt-get update
sudo apt-get install python3-opencv libopencv-dev python3-dev

# Instalar dependencias de Python
pip install -r requirements.txt
```

## 🎮 Uso

### Uso Rápido con Make (Recomendado)

```bash
# Instalación y verificación
make install     # Instalar todo automáticamente
make test        # Verificar que funciona

# Ejecutar detectores (elige uno)
make run-simple     # Detector básico
make run-enhanced   # Detector mejorado (RECOMENDADO)
make run-full       # Detector completo  
make run-demo       # Demo avanzado
make collect        # Recopilar datos
```

### 1. Detector Simple (Rápido de probar)

```bash
# Activar entorno virtual
source food_detection_env/bin/activate

# Ejecutar detector simple
python3 simple_food_detector.py
```

**Controles:**
- `q`: Salir del programa

### 3. Detector Mejorado (NUEVO - Recomendado)

```bash
# Activar entorno virtual
source food_detection_env/bin/activate

# Ejecutar detector mejorado
python3 enhanced_food_detector.py
```

**Controles:**
- `q`: Salir del programa
- `s`: Tomar screenshot con información detallada
- `c`: Mostrar estadísticas en consola

**Características especiales:**
- Detecta alimentos + bebidas + utensilios + contexto
- Umbrales de confianza inteligentes por categoría
- Información detallada por categorías
- Estadísticas en tiempo real

### 4. Detector Completo (Con más funciones)

```bash
# Activar entorno virtual
source food_detection_env/bin/activate

# Ejecutar detector completo
python3 food_detector.py
```

**Controles:**
- `q`: Salir del programa
- `s`: Tomar screenshot con detecciones

### 5. Recopilador de Datos

```bash
# Activar entorno virtual
source food_detection_env/bin/activate

# Ejecutar recopilador de datos
python3 food_data_collector.py
```

## 📁 Estructura del Proyecto

```
Gabinet_Cam/
├── requirements.txt              # Dependencias de Python
├── install.sh                   # Script de instalación automática
├── README.md                    # Este archivo
├── simple_food_detector.py      # Detector simple y rápido
├── ultra_simple_detector.py     # Detector ultra-simple (todo en uno)
├── enhanced_food_detector.py    # Detector mejorado (NUEVO - Recomendado)
├── food_detector.py             # Detector completo con funciones avanzadas
├── food_data_collector.py       # Recopilador de datos y estadísticas
├── demo.py                      # Demo avanzado con controles
├── config.py                    # Configuraciones centralizadas
├── utils.py                     # Utilidades y funciones helper
├── Makefile                     # Comandos simplificados
├── test.sh                      # Script de verificación
└── food_detection_env/          # Entorno virtual (se crea al instalar)
```

## ⚙️ Configuración

### Cambiar Cámara

Para usar una cámara diferente, modifica el índice en el código:

```python
# En cualquier archivo .py, busca:
cv2.VideoCapture(0)  # Cambiar 0 por 1, 2, etc.
```

### Ajustar Confianza

Para cambiar el umbral de confianza:

```python
# En food_detector.py
detector = FoodDetector(confidence_threshold=0.7)  # Cambiar 0.5 por el valor deseado
```

### Cambiar Modelo YOLO

Puedes usar diferentes modelos YOLO:

```python
# Modelos disponibles: yolov8n.pt (rápido), yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt (preciso)
detector = FoodDetector(model_path="yolov8s.pt")
```

## 📊 Salidas del Sistema

### Screenshots
- Se guardan como `food_detection_[timestamp].jpg`
- Incluyen todas las detecciones visibles

### Datos de Detección
- `detections_[timestamp].txt`: Lista de alimentos detectados
- `food_detections.json`: Datos detallados en formato JSON
- `detection_report.json`: Reporte estadístico

### Ejemplo de Reporte
```json
{
  "summary": {
    "total_frames_with_detections": 45,
    "total_food_detections": 123,
    "unique_foods_detected": 5,
    "average_detections_per_frame": 2.73
  },
  "food_frequency": {
    "apple": 34,
    "banana": 28,
    "orange": 21,
    "pizza": 15,
    "sandwich": 8
  }
}
```

## 🐛 Solución de Problemas

### Error: "No se pudo abrir la cámara"
```bash
# Verificar cámaras disponibles
ls /dev/video*

# Probar con diferentes índices
# Cambiar cv2.VideoCapture(0) por cv2.VideoCapture(1), etc.
```

### Error: "Import cv2 could not be resolved"
```bash
# Verificar que el entorno virtual está activado
source food_detection_env/bin/activate

# Reinstalar OpenCV
pip install opencv-python
```

### Baja velocidad de detección
```bash
# Usar modelo más pequeño
# En el código, cambiar "yolov8n.pt" por "yolov8n.pt" (ya es el más pequeño)
# O reducir resolución de cámara en el código
```

### Instalación fallida
```bash
# Instalar dependencias del sistema manualmente
sudo apt-get update
sudo apt-get install python3-pip python3-venv python3-opencv libopencv-dev

# Crear nuevo entorno virtual
rm -rf food_detection_env
python3 -m venv food_detection_env
source food_detection_env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 🔄 Actualizaciones Futuras

- [ ] Detección de alimentos personalizados
- [ ] Interfaz gráfica (GUI)
- [ ] Análisis nutricional básico
- [ ] Contador de calorías
- [ ] Guardado automático en base de datos
- [ ] API REST para integración
- [ ] Soporte para múltiples cámaras
- [ ] Detección de porciones

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para contribuir:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo `LICENSE` para detalles.

## 🙏 Agradecimientos

- [Ultralytics](https://ultralytics.com/) por YOLO
- [OpenCV](https://opencv.org/) por la biblioteca de visión por computadora
- Dataset COCO por las clases de alimentos

## 📞 Soporte

Si encuentras algún problema o tienes preguntas:

1. Revisa la sección de **Solución de Problemas**
2. Busca en los issues existentes
3. Crea un nuevo issue con detalles del problema

---

¡Disfruta detectando alimentos con IA! 🤖🍎
