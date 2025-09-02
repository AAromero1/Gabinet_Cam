#!/bin/bash

# Script de instalación para el proyecto de detección de alimentos

echo "🍎 Instalando dependencias para detección de alimentos con YOLO..."

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado. Por favor instala Python3 primero."
    exit 1
fi

# Verificar si pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 no está instalado. Instalando pip..."
    sudo apt-get update
    sudo apt-get install python3-pip -y
fi

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv food_detection_env

# Activar entorno virtual
echo "🔄 Activando entorno virtual..."
source food_detection_env/bin/activate

# Actualizar pip
echo "⬆️ Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias del sistema para OpenCV
echo "🔧 Instalando dependencias del sistema..."
sudo apt-get update
sudo apt-get install -y python3-opencv libopencv-dev python3-dev

# Instalar dependencias de Python
echo "📚 Instalando dependencias de Python..."
pip install -r requirements.txt

# Verificar instalación
echo "✅ Verificando instalación..."
python3 -c "import cv2; print(f'OpenCV version: {cv2.__version__}')"
python3 -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python3 -c "from ultralytics import YOLO; print('YOLO instalado correctamente')"

echo "🎉 ¡Instalación completada!"
echo ""
echo "🍎🥤 Para usar el detector de alimentos y objetos:"
echo "1. Activa el entorno virtual: source food_detection_env/bin/activate"
echo "2. Ejecuta el detector simple: python3 simple_food_detector.py"
echo "3. O ejecuta el detector mejorado: python3 enhanced_food_detector.py (RECOMENDADO)"
echo "4. O ejecuta el detector completo: python3 food_detector.py"
echo ""
echo "🚀 Uso rápido con Make:"
echo "   make run-simple     # Detector básico"
echo "   make run-enhanced   # Detector mejorado (alimentos + objetos)"
echo "   make run-demo       # Demo avanzado"
echo ""
echo "Para desactivar el entorno virtual: deactivate"
