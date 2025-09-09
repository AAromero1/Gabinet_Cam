#!/usr/bin/env python3
"""
Prueba completa del sistema de inventario con Google Sheets
- Agregar 3 productos al inventario
- Eliminar 2 productos para simular salida
- Actualizar hoja de sinónimos con términos acotados
"""

import logging
import time
from datetime import datetime
from google_sheets_integration import GoogleSheetsManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Ejecutar prueba completa del sistema de inventario"""
    
    print("🚀 Iniciando prueba completa del sistema de inventario...")
    print("=" * 60)
    
    # Inicializar el manager
    manager = GoogleSheetsManager()
    
    if not manager.is_connected:
        print("❌ No se pudo conectar a Google Sheets")
        return
    
    print(f"✅ Conectado exitosamente")
    print(f"📊 Spreadsheet: {manager.spreadsheet.title}")
    print(f"🔗 URL: {manager.spreadsheet.url}")
    print()
    
    # Mostrar estructura actual
    print("📋 Estructura detectada:")
    for sheet_name, info in manager.sheet_structure.items():
        print(f"  📄 {sheet_name}: {len(info['headers'])} columnas, {info['data_rows']} filas de datos")
    print()
    
    # FASE 1: Agregar 3 productos
    print("🔥 FASE 1: Agregando 3 productos al inventario...")
    print("-" * 50)
    
    productos_nuevos = [
        {
            'name': 'galletas_chocolate',
            'confidence': 0.925,
            'info': 'Galletas de chocolate marca Oreo detectadas por cámara'
        },
        {
            'name': 'bebida_cocacola',
            'confidence': 0.890,
            'info': 'Lata de Coca-Cola 350ml detectada'
        },
        {
            'name': 'snack_papas',
            'confidence': 0.875,
            'info': 'Bolsa de papas fritas Pringles detectada'
        }
    ]
    
    items_agregados = []
    
    for i, producto in enumerate(productos_nuevos, 1):
        print(f"📦 {i}/3 Agregando: {producto['name']}")
        
        success = manager.log_detection(
            item_name=producto['name'],
            confidence=producto['confidence'],
            additional_info=producto['info']
        )
        
        if success:
            # Obtener el item_id generado (último registro)
            data = manager.read_existing_data()
            if data:
                ultimo_item = data[-1]
                item_id = ultimo_item.get('item_id', f"DET_{int(time.time())}")
                items_agregados.append({
                    'item_id': item_id,
                    'name': producto['name'],
                    'confidence': producto['confidence']
                })
                print(f"  ✅ Producto agregado con ID: {item_id}")
            else:
                print(f"  ⚠️ No se pudo obtener el ID del producto")
        else:
            print(f"  ❌ Error agregando producto")
        
        time.sleep(1)  # Pausa entre inserciones
    
    print(f"\n📊 Productos agregados: {len(items_agregados)}")
    print()
    
    # FASE 2: Actualizar hoja de sinónimos
    print("🔗 FASE 2: Actualizando hoja de sinónimos...")
    print("-" * 50)
    
    if items_agregados:
        # Agregar sinónimos para cada producto usando el método del manager
        sinonimos_data = [
            ('galleta', items_agregados[0]['item_id'] if len(items_agregados) > 0 else 'DET_001', 'Snacks'),
            ('chocolate', items_agregados[0]['item_id'] if len(items_agregados) > 0 else 'DET_001', 'Snacks'),
            ('bebida', items_agregados[1]['item_id'] if len(items_agregados) > 1 else 'DET_002', 'Bebidas'),
            ('cocacola', items_agregados[1]['item_id'] if len(items_agregados) > 1 else 'DET_002', 'Bebidas'),
            ('snack', items_agregados[2]['item_id'] if len(items_agregados) > 2 else 'DET_003', 'Snacks'),
            ('papas', items_agregados[2]['item_id'] if len(items_agregados) > 2 else 'DET_003', 'Snacks')
        ]
        
        for i, (termino, item_id, categoria) in enumerate(sinonimos_data, 1):
            success = manager.add_synonym(termino, item_id, categoria)
            if success:
                print(f"  ✅ {i}/6 Sinónimo agregado: '{termino}' -> {item_id}")
            else:
                print(f"  ❌ {i}/6 Error agregando sinónimo: '{termino}'")
            time.sleep(0.5)  # Pausa para evitar rate limiting
    else:
        print("⚠️ No hay productos para agregar sinónimos")
    
    print()
    
    # FASE 3: Simular eliminación de 2 productos
    print("🗑️ FASE 3: Simulando eliminación de 2 productos...")
    print("-" * 50)
    
    if len(items_agregados) >= 2:
        # Productos a eliminar (los primeros 2)
        productos_a_eliminar = items_agregados[:2]
        
        for i, producto in enumerate(productos_a_eliminar, 1):
            print(f"🗑️ {i}/2 Eliminando: {producto['name']} (ID: {producto['item_id']})")
            
            # 1. Registrar en bitácora antes de eliminar
            bitacora_success = manager.log_removal_to_bitacora(
                item_id=producto['item_id'],
                item_name=producto['name'],
                reason="simulacion_salida_producto"
            )
            
            if bitacora_success:
                print(f"  ✅ Eliminación registrada en bitácora")
            else:
                print(f"  ⚠️ Error registrando en bitácora")
            
            # 2. Eliminar del inventario
            removal_success = manager.remove_item_from_inventory(
                item_id=producto['item_id'],
                reason="simulacion_salida_producto"
            )
            
            if removal_success:
                print(f"  ✅ Producto eliminado del inventario")
            else:
                print(f"  ❌ Error eliminando del inventario")
            
            time.sleep(1.5)  # Pausa entre eliminaciones
    else:
        print("⚠️ No hay suficientes productos para eliminar")
    
    print()
    
    # FASE 4: Mostrar resumen final
    print("📊 FASE 4: Resumen final del sistema...")
    print("-" * 50)
    
    try:
        # Contar registros en cada hoja
        inventario_data = manager.read_existing_data("Inventario") if "Inventario" in manager.sheet_structure else []
        
        # Contar sinónimos
        sinonimos_count = 0
        try:
            sinonimos_sheet = manager.spreadsheet.worksheet("Sinonimos")
            sinonimos_values = sinonimos_sheet.get_all_values()
            sinonimos_count = len([row for row in sinonimos_values[1:] if any(cell.strip() for cell in row)])
        except:
            pass
        
        # Contar bitácora
        bitacora_count = 0
        try:
            bitacora_sheet = manager.spreadsheet.worksheet("Bitacora")
            bitacora_values = bitacora_sheet.get_all_values()
            bitacora_count = len([row for row in bitacora_values[1:] if any(cell.strip() for cell in row)])
        except:
            pass
        
        print(f"📦 Inventario: {len(inventario_data)} items")
        print(f"🔗 Sinónimos: {sinonimos_count} términos")
        print(f"📝 Bitácora: {bitacora_count} eventos")
        print()
        print(f"🔗 URL del spreadsheet: {manager.spreadsheet.url}")
        print()
        
        # Mostrar últimos 3 registros del inventario
        if len(inventario_data) > 0:
            print("📋 Últimos registros del inventario:")
            for item in inventario_data[-3:]:
                name = item.get('name', 'N/A')
                item_id = item.get('item_id', 'N/A')
                category = item.get('category', 'N/A')
                print(f"  • {name} (ID: {item_id}, Categoría: {category})")
        
    except Exception as e:
        print(f"❌ Error generando resumen: {e}")
    
    print()
    print("🎉 Prueba completa finalizada exitosamente!")
    print("=" * 60)

if __name__ == "__main__":
    main()
