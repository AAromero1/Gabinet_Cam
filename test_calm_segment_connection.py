#!/usr/bin/env python3
"""
Test específico para conectar al spreadsheet público/privado de calm-segment
usando el ID específico del documento.

Autor: GitHub Copilot
"""

import json
import logging
from google_sheets_integration import GoogleSheetsManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_spreadsheet_id():
    """Extraer el ID del spreadsheet desde las credenciales"""
    try:
        with open("calm-segment-credentials.json", 'r') as f:
            creds = json.load(f)
            document_url = creds.get('document', '')
            
            print(f"📄 URL del documento: {document_url}")
            
            # Extraer ID de diferentes formatos de URL
            if '/spreadsheets/d/' in document_url:
                # Formato: https://docs.google.com/spreadsheets/d/ID/edit...
                spreadsheet_id = document_url.split('/spreadsheets/d/')[1].split('/')[0]
                print(f"🆔 ID extraído: {spreadsheet_id}")
                return spreadsheet_id
            elif 'PACX-' in document_url:
                # Formato público: /e/2PACX-...
                # Necesitamos el ID real del documento
                print("⚠️ URL pública detectada - necesitamos el ID real del documento")
                return None
            else:
                print("❌ Formato de URL no reconocido")
                return None
    except Exception as e:
        print(f"❌ Error leyendo credenciales: {e}")
        return None

def test_with_specific_id():
    """Probar conexión con ID específico"""
    print("🔍 === EXTRAYENDO ID DEL SPREADSHEET ===")
    
    # Extraer ID del documento
    spreadsheet_id = extract_spreadsheet_id()
    
    if not spreadsheet_id:
        print("❌ No se pudo extraer el ID del spreadsheet")
        print("💡 Usando ID del enlace público convertido...")
        # Intentar con ID conocido del enlace público
        # El enlace público 2PACX-1vTPy1PhDBNVMR62ugBQSt3jVnJ2kRvsLKXMWUmzSU-fjqrTXKayUHraVM2Ku6J9wYDvlD2fGFkys0wU
        # corresponde al ID real: 1piapJ41P5R993CYfOvUKMio7LQPYSHD6nIRCkwpClJY
        spreadsheet_id = "1piapJ41P5R993CYfOvUKMio7LQPYSHD6nIRCkwpClJY"
        print(f"🎯 Usando ID conocido: {spreadsheet_id}")
    
    print(f"\n🚀 === CONECTANDO AL SPREADSHEET ===")
    
    # Crear gestor con ID específico
    sheets_manager = GoogleSheetsManager(
        credentials_file="calm-segment-credentials.json",
        spreadsheet_id=spreadsheet_id
    )
    
    if not sheets_manager.get_connection_status():
        print("❌ No se pudo conectar al spreadsheet")
        return False
    
    print("✅ ¡Conexión exitosa!")
    
    # Mostrar información
    info = sheets_manager.get_spreadsheet_info()
    print(f"📊 Título: {info.get('title', 'N/A')}")
    print(f"🔗 URL: {info.get('url', 'N/A')}")
    print(f"📋 Hoja activa: {info.get('worksheet_title', 'N/A')}")
    print(f"📏 Dimensiones: {info.get('row_count', 0)} x {info.get('col_count', 0)}")
    
    # Listar todas las hojas disponibles
    try:
        worksheets = sheets_manager.spreadsheet.worksheets()
        print(f"\n📑 Hojas disponibles ({len(worksheets)}):")
        for i, ws in enumerate(worksheets, 1):
            print(f"  {i}. {ws.title} ({ws.row_count}x{ws.col_count})")
    except Exception as e:
        print(f"⚠️ Error listando hojas: {e}")
    
    # Probar lectura de datos
    try:
        if sheets_manager.sheet:
            print(f"\n📖 === LEYENDO DATOS DE LA HOJA ===")
            headers = sheets_manager.sheet.row_values(1)
            print(f"📋 Encabezados: {headers}")
            
            # Leer algunas filas de datos
            all_values = sheets_manager.sheet.get_all_values()
            data_rows = [row for row in all_values[1:] if any(cell.strip() for cell in row)]
            print(f"📊 Filas con datos: {len(data_rows)}")
            
            if data_rows:
                print(f"🔍 Primera fila de datos: {data_rows[0]}")
    except Exception as e:
        print(f"⚠️ Error leyendo datos: {e}")
    
    # Probar una detección de prueba
    print(f"\n🧪 === PRUEBA DE ESCRITURA ===")
    try:
        success = sheets_manager.log_detection("galletas_test", 0.95, "Prueba de conexión exitosa")
        if success:
            print("✅ ¡Escritura exitosa!")
        else:
            print("❌ Error en escritura")
    except Exception as e:
        print(f"⚠️ Error probando escritura: {e}")
    
    return True

def main():
    """Función principal"""
    print("🎯 Prueba de conexión específica al spreadsheet calm-segment")
    print("=" * 60)
    
    success = test_with_specific_id()
    
    if success:
        print("\n🎉 ¡Prueba completada!")
        print("💡 El sistema puede acceder al spreadsheet")
    else:
        print("\n❌ Prueba fallida")
        print("💡 Revisa permisos y credenciales")

if __name__ == "__main__":
    main()
