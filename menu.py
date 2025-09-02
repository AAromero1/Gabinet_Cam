#!/usr/bin/env python3
"""
Script de demostración que muestra las capacidades del sistema
"""

import time
import os

def print_banner():
    """Mostrar banner del sistema"""
    print("=" * 70)
    print("🍎🥤🍽️ DETECTOR DE ALIMENTOS Y OBJETOS CON YOLO")
    print("=" * 70)
    print("Un sistema completo para detectar:")
    print("  • Alimentos (frutas, comida preparada, postres)")
    print("  • Bebidas y contenedores (botellas, vasos)")
    print("  • Utensilios de cocina (bowls, cubiertos)")
    print("  • Objetos de contexto (laptop, teclado, libros)")
    print("=" * 70)

def show_menu():
    """Mostrar menú de opciones"""
    print("\n🎮 ¿Qué detector quieres probar?")
    print("1. 🚀 Detector Ultra-Simple (todo en un archivo)")
    print("2. ⚡ Detector Simple (básico y rápido)")
    print("3. 🌟 Detector Mejorado (RECOMENDADO - más objetos)")
    print("4. 🔧 Detector Completo (funciones avanzadas)")
    print("5. 🎯 Demo Avanzado (con estadísticas)")
    print("6. 📊 Recopilador de Datos")
    print("7. 🧪 Verificar Sistema")
    print("8. ❓ Ayuda")
    print("0. 👋 Salir")
    print("-" * 50)

def run_detector(choice):
    """Ejecutar el detector seleccionado"""
    detectors = {
        '1': ('ultra_simple_detector.py', 'Detector Ultra-Simple'),
        '2': ('simple_food_detector.py', 'Detector Simple'),
        '3': ('enhanced_food_detector.py', 'Detector Mejorado'),
        '4': ('food_detector.py', 'Detector Completo'),
        '5': ('demo.py', 'Demo Avanzado'),
        '6': ('food_data_collector.py', 'Recopilador de Datos')
    }
    
    if choice in detectors:
        script, name = detectors[choice]
        print(f"\n🚀 Iniciando {name}...")
        print("=" * 50)
        
        # Verificar si el entorno virtual está activado
        if 'food_detection_env' not in os.environ.get('VIRTUAL_ENV', ''):
            print("⚠️  IMPORTANTE: Activa el entorno virtual primero:")
            print("   source food_detection_env/bin/activate")
            print("")
        
        # Mostrar comando para ejecutar
        print(f"Ejecutando: python3 {script}")
        print("")
        print("💡 Consejos:")
        if choice == '3':
            print("  • Este detector es el MÁS COMPLETO")
            print("  • Detecta alimentos + bebidas + utensilios")
            print("  • Presiona 'c' para ver estadísticas")
        
        print("  • Presiona 'q' para salir")
        print("  • Presiona 's' para screenshot")
        print("  • Asegúrate de tener buena iluminación")
        print("=" * 50)
        
        try:
            os.system(f"python3 {script}")
        except KeyboardInterrupt:
            print("\n⚠️ Detector interrumpido por el usuario")
    
    elif choice == '7':
        verify_system()
    elif choice == '8':
        show_help()
    elif choice == '0':
        print("👋 ¡Gracias por usar el detector!")
        return False
    else:
        print("❌ Opción no válida")
    
    return True

def verify_system():
    """Verificar que el sistema esté configurado correctamente"""
    print("\n🧪 Verificando sistema...")
    print("=" * 30)
    
    # Verificar entorno virtual
    if os.path.exists('food_detection_env'):
        print("✅ Entorno virtual encontrado")
    else:
        print("❌ Entorno virtual no encontrado")
        print("   Ejecuta: ./install.sh")
        return
    
    # Verificar archivos principales
    important_files = [
        'enhanced_food_detector.py',
        'simple_food_detector.py', 
        'requirements.txt',
        'config.py'
    ]
    
    for file in important_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
    
    print("\n🔧 Para verificación completa ejecuta:")
    print("   ./test.sh")

def show_help():
    """Mostrar ayuda"""
    print("\n❓ AYUDA - Detector de Alimentos y Objetos")
    print("=" * 50)
    print("🎯 OBJETIVO:")
    print("  Detectar alimentos y objetos relacionados en tiempo real")
    print("  usando inteligencia artificial (YOLO) y tu webcam.")
    print("")
    print("🚀 INICIO RÁPIDO:")
    print("  1. Ejecuta: ./install.sh")
    print("  2. Ejecuta: python3 menu.py")
    print("  3. Elige opción 3 (Detector Mejorado)")
    print("")
    print("🍎 QUÉ DETECTA:")
    print("  • Alimentos: banana, manzana, pizza, sandwich, etc.")
    print("  • Bebidas: botellas, vasos, tazas")
    print("  • Utensilios: bowls, tenedores, cuchillos, cucharas")
    print("  • Contexto: laptop, teclado (para snacking)")
    print("")
    print("🎮 CONTROLES:")
    print("  • Q: Salir")
    print("  • S: Tomar screenshot")
    print("  • C: Estadísticas (en detector mejorado)")
    print("")
    print("🔧 SOLUCIÓN DE PROBLEMAS:")
    print("  • No detecta nada: Mejora la iluminación")
    print("  • Error de cámara: Verifica que no esté siendo usada")
    print("  • Error de importación: Ejecuta ./install.sh")
    print("=" * 50)

def main():
    """Función principal del menú"""
    print_banner()
    
    # Verificar instalación básica
    if not os.path.exists('food_detection_env'):
        print("❌ Sistema no instalado.")
        print("🔧 Ejecuta primero: ./install.sh")
        return
    
    while True:
        show_menu()
        try:
            choice = input("\n👆 Elige una opción (0-8): ").strip()
            
            if not run_detector(choice):
                break
                
            # Pausa entre ejecuciones
            if choice in ['1', '2', '3', '4', '5', '6']:
                input("\n📱 Presiona Enter para volver al menú...")
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()
