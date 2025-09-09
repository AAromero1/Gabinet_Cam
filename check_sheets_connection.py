from google_sheets_integration import GoogleSheetsManager

print("🔍 VERIFICANDO CONEXIÓN A GOOGLE SHEETS")
print("=" * 40)

try:
    gm = GoogleSheetsManager()
    print(f"Estado de conexión: {'✅ CONECTADO' if gm.is_connected else '❌ DESCONECTADO'}")
    
    if gm.is_connected:
        try:
            info = gm.get_spreadsheet_info()
            print(f"Título: {info.get('title', 'N/A')}")
            print(f"Registros: {info.get('data_rows', 0)}")
            print(f"URL: {gm.get_spreadsheet_url()}")
        except Exception as e:
            print(f"Error obteniendo info: {e}")
    else:
        print("❌ No se pudo conectar a Google Sheets")
        print("Verifica el archivo calm-segment-credentials.json")

except Exception as e:
    print(f"❌ Error al importar o conectar: {e}")

print("=" * 40)
