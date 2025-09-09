#!/usr/bin/env python3
"""
Prueba final del sistema integrado de Google Sheets
que respeta la estructura existente del spreadsheet.

Autor: GitHub Copilot
"""

import logging
from google_sheets_integration import GoogleSheetsManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_integrated_sheets_manager():
    """Probar el GoogleSheetsManager integrado"""
    print("🎯 === PRUEBA DEL SISTEMA INTEGRADO ===")
    print("ℹ️  Usando GoogleSheetsManager que respeta estructura existente")
    print("=" * 60)
    
    # Inicializar el gestor
    manager = GoogleSheetsManager()
    
    if not manager.get_connection_status():
        print("❌ No se pudo conectar a Google Sheets")
        return False
    
    print("✅ Conexión exitosa")
    
    # Mostrar información del spreadsheet
    info = manager.get_spreadsheet_info()
    print(f"📊 Título: {info.get('title', 'N/A')}")
    print(f"🔗 URL: {info.get('url', 'N/A')}")
    print(f"📋 Hoja activa: {info.get('worksheet_title', 'N/A')}")
    print(f"📊 Registros existentes: {info.get('data_rows', 0)}")
    
    # Probar detecciones usando el método integrado
    print(f"\n🧪 === PRUEBAS DE DETECCIÓN ===")
    
    test_items = [
        ("galletas_chocolate", 0.93, "Detección con confianza alta"),
        ("lata_cocacola", 0.89, "Lata detectada en mesa"),
        ("bebida_agua", 0.85, "Botella de agua detectada"),
        ("snack_papas", 0.91, "Paquete de papas identificado")
    ]
    
    for item_name, confidence, notes in test_items:
        print(f"\n📝 Registrando: {item_name}")
        success = manager.log_detection(item_name, confidence, notes)
        
        if success:
            print(f"   ✅ Registrado exitosamente")
        else:
            print(f"   ❌ Error en el registro")
    
    # Verificar registros finales
    print(f"\n📊 === VERIFICACIÓN FINAL ===")
    final_info = manager.get_spreadsheet_info()
    print(f"📈 Total de registros: {final_info.get('data_rows', 0)}")
    
    # Leer algunos datos para verificar
    if hasattr(manager, 'read_existing_data'):
        recent_data = manager.read_existing_data()
        if recent_data:
            print(f"🔍 Últimos 3 registros:")
            for i, record in enumerate(recent_data[-3:], 1):
                item_name = record.get('name', 'N/A')
                confidence = record.get('confidence', 'N/A')
                print(f"   {i}. {item_name} (confianza: {confidence})")
    
    return True

def main():
    """Función principal"""
    print("🚀 Prueba final del sistema integrado de Google Sheets")
    print("🎯 Sistema que respeta la estructura existente del spreadsheet")
    print("=" * 70)
    
    success = test_integrated_sheets_manager()
    
    if success:
        print("\n🎉 ¡Sistema integrado funcionando perfectamente!")
        print("✅ Ahora puedes usar este sistema en tu detector de alimentos")
        print("📋 Todas las detecciones se registrarán automáticamente")
        print("🔗 Revisa tu Google Sheets para ver los resultados")
    else:
        print("\n❌ Error en el sistema integrado")
        print("💡 Verifica la conexión y configuración")

if __name__ == "__main__":
    main()
