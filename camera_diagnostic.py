#!/usr/bin/env python3
"""
Script de diagnóstico para cámaras USB
"""

import cv2
import os
import subprocess
import sys

def print_header():
    print("="*60)
    print("🔍 DIAGNÓSTICO DE CÁMARA USB")
    print("="*60)

def check_video_devices():
    """Verificar dispositivos de video disponibles"""
    print("1. 📹 Verificando dispositivos de video...")
    
    try:
        # Verificar /dev/video*
        video_devices = []
        for i in range(10):
            device_path = f"/dev/video{i}"
            if os.path.exists(device_path):
                video_devices.append(device_path)
        
        if video_devices:
            print(f"   ✅ Dispositivos encontrados: {video_devices}")
        else:
            print("   ❌ No se encontraron dispositivos /dev/video*")
            
        return video_devices
    except Exception as e:
        print(f"   ❌ Error verificando dispositivos: {e}")
        return []

def check_usb_devices():
    """Verificar dispositivos USB"""
    print("2. 🔌 Verificando dispositivos USB...")
    
    try:
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            camera_devices = [line for line in lines if any(keyword in line.lower() 
                            for keyword in ['camera', 'webcam', 'video', 'imaging'])]
            
            if camera_devices:
                print("   ✅ Dispositivos USB relacionados con cámara:")
                for device in camera_devices:
                    print(f"      {device}")
            else:
                print("   ⚠️  No se encontraron cámaras USB específicas")
                print("   📋 Todos los dispositivos USB:")
                for line in lines:
                    print(f"      {line}")
        else:
            print("   ❌ No se pudo ejecutar lsusb")
    except Exception as e:
        print(f"   ❌ Error verificando USB: {e}")

def test_opencv_cameras():
    """Probar cámaras con OpenCV"""
    print("3. 📷 Probando cámaras con OpenCV...")
    
    working_cameras = []
    
    # Probar índices numéricos
    for i in range(5):
        try:
            print(f"   Probando índice {i}...")
            cap = cv2.VideoCapture(i)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    print(f"   ✅ Cámara {i}: Funcional ({width}x{height})")
                    working_cameras.append(i)
                else:
                    print(f"   ⚠️  Cámara {i}: Se abre pero no puede leer frames")
                cap.release()
            else:
                print(f"   ❌ Cámara {i}: No se puede abrir")
                
        except Exception as e:
            print(f"   ❌ Error probando cámara {i}: {e}")
    
    # Probar rutas de dispositivos
    video_devices = [f"/dev/video{i}" for i in range(5) if os.path.exists(f"/dev/video{i}")]
    for device in video_devices:
        try:
            print(f"   Probando dispositivo {device}...")
            cap = cv2.VideoCapture(device)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    print(f"   ✅ {device}: Funcional ({width}x{height})")
                    working_cameras.append(device)
                else:
                    print(f"   ⚠️  {device}: Se abre pero no puede leer frames")
                cap.release()
            else:
                print(f"   ❌ {device}: No se puede abrir")
                
        except Exception as e:
            print(f"   ❌ Error probando {device}: {e}")
    
    return working_cameras

def check_permissions():
    """Verificar permisos de dispositivos de video"""
    print("4. 🔐 Verificando permisos...")
    
    video_devices = [f"/dev/video{i}" for i in range(5) if os.path.exists(f"/dev/video{i}")]
    
    if not video_devices:
        print("   ⚠️  No hay dispositivos de video para verificar permisos")
        return
    
    for device in video_devices:
        try:
            stat_info = os.stat(device)
            permissions = oct(stat_info.st_mode)[-3:]
            print(f"   {device}: permisos {permissions}")
            
            if os.access(device, os.R_OK | os.W_OK):
                print(f"   ✅ {device}: Acceso de lectura/escritura OK")
            else:
                print(f"   ❌ {device}: Sin acceso de lectura/escritura")
                
        except Exception as e:
            print(f"   ❌ Error verificando permisos de {device}: {e}")

def suggest_solutions(working_cameras):
    """Sugerir soluciones basadas en los resultados"""
    print("\n" + "="*60)
    print("💡 SUGERENCIAS DE SOLUCIÓN")
    print("="*60)
    
    if working_cameras:
        print("✅ ¡Buenas noticias! Se encontraron cámaras funcionales:")
        for cam in working_cameras:
            print(f"   📷 {cam}")
        print("\n🔧 Para usar en el detector:")
        print("   1. Edita el código para usar estos índices específicos")
        print("   2. O ejecuta el detector mejorado que prueba automáticamente")
        return
    
    print("❌ No se encontraron cámaras funcionales. Soluciones:")
    print("\n1. 🔌 Verificar conexión física:")
    print("   • Desconecta y reconecta la cámara USB")
    print("   • Prueba otro puerto USB (preferiblemente USB 2.0)")
    print("   • Verifica que la cámara tenga alimentación suficiente")
    
    print("\n2. 📦 Instalar software de prueba:")
    print("   sudo apt-get update")
    print("   sudo apt-get install cheese guvcview v4l-utils")
    print("   cheese  # Probar la cámara")
    
    print("\n3. 🔐 Solucionar permisos:")
    print("   sudo chmod 666 /dev/video*")
    print("   # O añadir usuario al grupo video:")
    print("   sudo usermod -a -G video $USER")
    print("   # Luego reiniciar sesión")
    
    print("\n4. 🔄 Reiniciar drivers:")
    print("   sudo modprobe -r uvcvideo")
    print("   sudo modprobe uvcvideo")
    
    print("\n5. 🐧 Verificar compatibilidad:")
    print("   lsusb -v | grep -A5 -B5 -i video")
    print("   dmesg | grep -i video")

def test_specific_camera():
    """Probar una cámara específica de forma interactiva"""
    print("\n" + "="*60)
    print("🎯 PRUEBA INTERACTIVA")
    print("="*60)
    
    while True:
        try:
            camera_input = input("\n¿Qué cámara quieres probar? (índice o 'q' para salir): ").strip()
            
            if camera_input.lower() == 'q':
                break
            
            # Intentar convertir a entero
            try:
                camera_index = int(camera_input)
            except ValueError:
                camera_index = camera_input  # Podría ser una ruta como /dev/video0
            
            print(f"Probando cámara: {camera_index}")
            
            cap = cv2.VideoCapture(camera_index)
            
            if not cap.isOpened():
                print("❌ No se pudo abrir la cámara")
                continue
            
            print("✅ Cámara abierta. Presiona 'q' para salir, 's' para screenshot")
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    print("❌ No se pudo leer frame")
                    break
                
                frame_count += 1
                
                # Añadir información al frame
                cv2.putText(frame, f"Camera {camera_index} - Frame {frame_count}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "Presiona 'q' para salir, 's' para screenshot", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                cv2.imshow(f'Test Camera {camera_index}', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    filename = f"test_camera_{camera_index}_{frame_count}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"📸 Screenshot guardado: {filename}")
            
            cap.release()
            cv2.destroyAllWindows()
            
        except KeyboardInterrupt:
            print("\n⚠️ Prueba interrumpida")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Función principal del diagnóstico"""
    print_header()
    
    # Verificar que OpenCV esté disponible
    try:
        print(f"OpenCV version: {cv2.__version__}")
    except Exception as e:
        print(f"❌ Error con OpenCV: {e}")
        return
    
    print()
    
    # Ejecutar diagnósticos
    video_devices = check_video_devices()
    print()
    
    check_usb_devices()
    print()
    
    working_cameras = test_opencv_cameras()
    print()
    
    check_permissions()
    
    # Sugerir soluciones
    suggest_solutions(working_cameras)
    
    # Ofrecer prueba interactiva
    if working_cameras:
        response = input("\n¿Quieres probar una cámara de forma interactiva? (y/n): ").strip().lower()
        if response == 'y':
            test_specific_camera()

if __name__ == "__main__":
    main()
