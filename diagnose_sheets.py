#!/usr/bin/env python3
"""
Script de diagnóstico detallado para Google Sheets
"""

import os
import json
import time
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

def diagnose_google_sheets():
    """Diagnóstico completo de la conexión a Google Sheets"""
    
    print("🔍 DIAGNÓSTICO DETALLADO DE GOOGLE SHEETS")
    print("=" * 50)
    
    # 1. Verificar archivo de credenciales
    credentials_file = "calm-segment-credentials.json"
    print(f"1. Verificando archivo: {credentials_file}")
    
    if not os.path.exists(credentials_file):
        print(f"❌ Archivo no encontrado: {credentials_file}")
        return False
    
    print(f"✅ Archivo encontrado: {os.path.getsize(credentials_file)} bytes")
    
    # 2. Verificar contenido del archivo
    try:
        with open(credentials_file, 'r') as f:
            creds_data = json.load(f)
        
        print("✅ Archivo JSON válido")
        
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in creds_data]
        
        if missing_fields:
            print(f"❌ Campos faltantes: {missing_fields}")
            return False
        
        print(f"✅ Campos requeridos presentes")
        print(f"   • Proyecto: {creds_data.get('project_id', 'N/A')}")
        print(f"   • Email: {creds_data.get('client_email', 'N/A')}")
        print(f"   • Tipo: {creds_data.get('type', 'N/A')}")
        
        # Verificar URL del documento
        document_url = creds_data.get('document', '')
        if document_url:
            print(f"✅ URL del documento: {document_url[:50]}...")
            if '/spreadsheets/d/' in document_url:
                spreadsheet_id = document_url.split('/spreadsheets/d/')[1].split('/')[0]
                print(f"✅ ID extraído: {spreadsheet_id}")
            else:
                print("⚠️ URL no parece ser de Google Sheets")
        else:
            print("⚠️ No hay URL de documento en las credenciales")
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return False
    
    # 3. Verificar hora del sistema
    print(f"\n2. Verificando hora del sistema:")
    current_time = datetime.now()
    print(f"   • Hora local: {current_time}")
    print(f"   • Timestamp: {int(time.time())}")
    
    # 4. Intentar autenticación paso a paso
    print(f"\n3. Intentando autenticación:")
    
    try:
        # Definir scopes
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        print(f"✅ Scopes definidos: {len(scope)} scopes")
        
        # Cargar credenciales
        print("   • Cargando credenciales...")
        credentials = Credentials.from_service_account_file(
            credentials_file, scopes=scope
        )
        print("✅ Credenciales cargadas")
        
        # Verificar si las credenciales necesitan refresh
        if credentials.expired:
            print("⚠️ Credenciales expiradas, intentando refresh...")
            credentials.refresh()
            print("✅ Credenciales renovadas")
        
        # Crear cliente
        print("   • Creando cliente gspread...")
        client = gspread.authorize(credentials)
        print("✅ Cliente gspread creado")
        
        # Intentar acceder al documento
        if 'spreadsheet_id' in locals():
            print(f"   • Intentando acceder al documento {spreadsheet_id}...")
            try:
                sheet = client.open_by_key(spreadsheet_id)
                print(f"✅ Acceso exitoso al documento: {sheet.title}")
                
                # Listar hojas
                worksheets = sheet.worksheets()
                print(f"✅ Hojas encontradas: {len(worksheets)}")
                for i, ws in enumerate(worksheets):
                    print(f"     {i+1}. {ws.title} ({ws.row_count} filas)")
                
                return True
                
            except Exception as e:
                print(f"❌ Error accediendo al documento: {e}")
                print("   Posibles causas:")
                print("   - La cuenta de servicio no tiene acceso al documento")
                print("   - El documento no existe o fue eliminado")
                print("   - ID de documento incorrecto")
                return False
        else:
            print("⚠️ No se pudo extraer ID del documento")
            return False
        
    except Exception as e:
        print(f"❌ Error en autenticación: {e}")
        print(f"   Tipo de error: {type(e).__name__}")
        
        if "Invalid JWT Signature" in str(e):
            print("💡 SOLUCIONES PARA JWT SIGNATURE:")
            print("   1. Verificar que la hora del sistema esté sincronizada")
            print("   2. Regenerar las credenciales en Google Cloud Console")
            print("   3. Verificar que la cuenta de servicio esté activa")
            print("   4. Verificar que no haya caracteres extra en el private_key")
        
        return False

def main():
    success = diagnose_google_sheets()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 DIAGNÓSTICO EXITOSO - Google Sheets está funcionando")
    else:
        print("❌ DIAGNÓSTICO FALLIDO - Revisar los errores arriba")
        print("\n📋 PASOS RECOMENDADOS:")
        print("1. Ir a Google Cloud Console")
        print("2. Regenerar las credenciales de la cuenta de servicio")
        print("3. Descargar el nuevo archivo JSON")
        print("4. Reemplazar calm-segment-credentials.json")
        print("5. Asegurar que la cuenta tenga acceso al spreadsheet")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
