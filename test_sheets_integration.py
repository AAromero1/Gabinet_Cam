#!/usr/bin/env python3
"""
Script de prueba para verificar la integración con Google Sheets
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google_sheets_integration import GoogleSheetsManager, DetectionTracker
import logging
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_google_sheets_integration():
    """Probar la integración con Google Sheets"""
    print("🧪 PRUEBA DE INTEGRACIÓN GOOGLE SHEETS")
    print("=" * 50)
    
    # Crear manager de Google Sheets
    print("\n1. Inicializando Google Sheets Manager...")
    sheets_manager = GoogleSheetsManager()
    
    # Probar conexión
    print("\n2. Probando conexión...")
    if sheets_manager.test_connection():
        print("✅ Conexión exitosa!")
        
        # Obtener información detallada
        info = sheets_manager.get_spreadsheet_info()
        print(f"\n📊 Información del Spreadsheet:")
        print(f"   📋 Título: {info.get('title', 'N/A')}")
        print(f"   📏 Dimensiones: {info.get('row_count', 0)} x {info.get('col_count', 0)}")
        print(f"   📝 Filas con datos: {info.get('data_rows', 0)}")
        print(f"   📑 Encabezados: {info.get('headers', [])}")
        
        # Enviar detección de prueba
        print("\n3. Enviando detección de prueba...")
        test_detection = {
            'class_name': 'manzana_test',
            'category': 'fruta',
            'confidence': 0.95,
            'status': 'detectado',
            'duration_seconds': 0,
            'frames_detected': 1,
            'bbox': [100, 150, 200, 250],
            'area': 10000
        }
        
        success = sheets_manager.send_detection(test_detection)
        if success:
            print("✅ Detección de prueba enviada exitosamente!")
            
            # Actualizar estado después de 2 segundos
            time.sleep(2)
            print("\n4. Actualizando estado de la detección...")
            sheets_manager.update_detection_status('manzana_test', 'perdido', 2.0)
            print("✅ Estado actualizado!")
            
        else:
            print("❌ Error enviando detección de prueba")
            
    else:
        print("❌ No se pudo conectar a Google Sheets")
        print("💡 Verifica tu archivo de credenciales: calm-segment-credentials.json")
    
    print("\n5. Probando DetectionTracker...")
    tracker = DetectionTracker(stability_frames=5)  # Menos frames para prueba rápida
    
    # Simular algunas detecciones
    for i in range(10):
        simulated_detections = [
            {
                'class_name': 'banana',
                'category': 'fruta',
                'confidence': 0.8,
                'bbox': [50, 50, 150, 200],
                'area': 15000
            }
        ]
        tracker.update(simulated_detections)
        time.sleep(0.1)  # Simular frames
    
    stats = tracker.get_stats()
    print(f"📊 Estadísticas del Tracker:")
    print(f"   🔢 Frames procesados: {stats['frame_count']}")
    print(f"   ✅ Objetos activos: {stats['active_objects']}")
    print(f"   📤 Enviados a Sheets: {stats['sent_objects']}")
    print(f"   🔗 Conexión Sheets: {stats['sheets_connected']}")
    
    print("\n🎉 Prueba completada!")
    print("🔗 Revisa tu Google Spreadsheet para ver los resultados")

def create_test_credentials():
    """Crear archivo de credenciales de prueba"""
    print("📝 Creando archivo de credenciales de ejemplo...")
    
    template = {
        "type": "service_account",
        "project_id": "tu-proyecto-id-aqui",
        "private_key_id": "tu-private-key-id-aqui",
        "private_key": "-----BEGIN PRIVATE KEY-----\nTU_CLAVE_PRIVADA_COMPLETA_AQUI\n-----END PRIVATE KEY-----\n",
        "client_email": "tu-service-account@tu-proyecto.iam.gserviceaccount.com",
        "client_id": "tu-client-id-aqui",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/tu-service-account%40tu-proyecto.iam.gserviceaccount.com"
    }
    
    with open("calm-segment-credentials.json", 'w') as f:
        import json
        json.dump(template, f, indent=2)
    
    print("✅ Archivo 'calm-segment-credentials.json' creado!")
    print("🔧 Edita este archivo con tus credenciales reales de Google Cloud")
    print("📚 Guía: https://docs.gspread.org/en/latest/oauth2.html")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--create-credentials":
        create_test_credentials()
    else:
        test_google_sheets_integration()
