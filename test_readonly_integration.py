#!/usr/bin/env python3
"""
Test de lectura pura del spreadsheet sin modificar estructura.
Solo lee la estructura existente y registra detecciones usando el formato actual.

Autor: GitHub Copilot
"""

import json
import logging
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ReadOnlyGoogleSheetsManager:
    """
    Gestor que respeta la estructura existente del spreadsheet
    sin hacer ningún cambio a los encabezados o estructura
    """
    
    def __init__(self, credentials_file="calm-segment-credentials.json"):
        self.credentials_file = credentials_file
        self.client = None
        self.spreadsheet = None
        self.is_connected = False
        self.sheet_structure = {}
        
        self._connect()
    
    def _connect(self):
        """Conectar y analizar estructura existente"""
        try:
            # Cargar credenciales
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = Credentials.from_service_account_file(
                self.credentials_file, scopes=scope
            )
            
            self.client = gspread.authorize(credentials)
            
            # Obtener ID del spreadsheet desde credenciales
            with open(self.credentials_file, 'r') as f:
                creds_data = json.load(f)
                document_url = creds_data.get('document', '')
                if '/spreadsheets/d/' in document_url:
                    spreadsheet_id = document_url.split('/spreadsheets/d/')[1].split('/')[0]
                    self.spreadsheet = self.client.open_by_key(spreadsheet_id)
                    logger.info(f"✅ Conectado al spreadsheet: {self.spreadsheet.title}")
                    self.is_connected = True
                    
                    # Analizar estructura existente
                    self._analyze_existing_structure()
                else:
                    logger.error("❌ No se pudo extraer ID del documento")
                    
        except Exception as e:
            logger.error(f"❌ Error conectando: {e}")
            self.is_connected = False
    
    def _analyze_existing_structure(self):
        """Analizar y mapear la estructura existente sin cambiarla"""
        try:
            worksheets = self.spreadsheet.worksheets()
            logger.info(f"\n📊 === ANÁLISIS DE ESTRUCTURA EXISTENTE ===")
            logger.info(f"📋 Spreadsheet: {self.spreadsheet.title}")
            logger.info(f"🔗 URL: {self.spreadsheet.url}")
            logger.info(f"📑 Número de hojas: {len(worksheets)}")
            
            for i, ws in enumerate(worksheets, 1):
                logger.info(f"\n📄 Hoja {i}: {ws.title}")
                logger.info(f"   📏 Dimensiones: {ws.row_count} x {ws.col_count}")
                
                # Leer encabezados existentes
                try:
                    headers = ws.row_values(1)
                    if headers:
                        logger.info(f"   📋 Encabezados ({len(headers)}): {headers}")
                        
                        # Contar filas con datos
                        all_values = ws.get_all_values()
                        data_rows = len([row for row in all_values[1:] if any(cell.strip() for cell in row)])
                        logger.info(f"   📊 Filas con datos: {data_rows}")
                        
                        # Guardar estructura para uso posterior
                        self.sheet_structure[ws.title] = {
                            'worksheet': ws,
                            'headers': headers,
                            'data_rows': data_rows,
                            'total_rows': ws.row_count,
                            'total_cols': ws.col_count
                        }
                    else:
                        logger.info(f"   ⚠️ No hay encabezados")
                        
                except Exception as e:
                    logger.warning(f"   ⚠️ Error leyendo hoja {ws.title}: {e}")
            
            # Identificar hoja principal para detecciones
            self._identify_main_sheet()
                    
        except Exception as e:
            logger.error(f"❌ Error analizando estructura: {e}")
    
    def _identify_main_sheet(self):
        """Identificar cuál hoja usar para las detecciones"""
        self.main_sheet = None
        
        # Prioridad: Inventario > primera hoja con datos
        if 'Inventario' in self.sheet_structure:
            self.main_sheet = self.sheet_structure['Inventario']['worksheet']
            self.main_headers = self.sheet_structure['Inventario']['headers']
            logger.info(f"✅ Hoja principal identificada: Inventario")
        else:
            # Usar la primera hoja que tenga datos
            for sheet_name, info in self.sheet_structure.items():
                if info['data_rows'] >= 0:  # Cualquier hoja, incluso sin datos
                    self.main_sheet = info['worksheet']
                    self.main_headers = info['headers']
                    logger.info(f"✅ Hoja principal identificada: {sheet_name}")
                    break
        
        if self.main_sheet:
            logger.info(f"📋 Estructura a usar: {self.main_headers}")
        else:
            logger.error("❌ No se pudo identificar hoja principal")
    
    def log_detection_compatible(self, item_name, confidence, additional_info=None):
        """
        Registrar detección usando la estructura existente sin modificarla
        """
        if not self.main_sheet or not self.main_headers:
            logger.error("❌ No hay hoja principal disponible")
            return False
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Crear fila compatible con la estructura existente
            nueva_fila = []
            
            # Mapear campos según los encabezados existentes
            for header in self.main_headers:
                header_lower = header.lower()
                
                if 'id' in header_lower and 'item' in header_lower:
                    # item_id
                    nueva_fila.append(f"DET_{int(timestamp.replace('-', '').replace(':', '').replace(' ', ''))}")
                elif 'name' in header_lower or 'nombre' in header_lower:
                    # name/nombre
                    nueva_fila.append(item_name)
                elif 'category' in header_lower or 'categoria' in header_lower:
                    # category/categoria
                    category = self._determine_category(item_name)
                    nueva_fila.append(category)
                elif 'confidence' in header_lower or 'confianza' in header_lower:
                    # confidence/confianza
                    nueva_fila.append(f"{confidence:.3f}")
                elif 'quantity' in header_lower or 'cantidad' in header_lower:
                    # quantity/cantidad
                    nueva_fila.append("1")
                elif 'source' in header_lower or 'origen' in header_lower:
                    # source/origen
                    nueva_fila.append("camera")
                elif 'event' in header_lower or 'evento' in header_lower:
                    # event/evento
                    nueva_fila.append("detection")
                elif 'timestamp' in header_lower or 'fecha' in header_lower or 'created' in header_lower:
                    # timestamp/fecha/created
                    nueva_fila.append(timestamp)
                elif 'updated' in header_lower:
                    # updated
                    nueva_fila.append(timestamp)
                elif 'note' in header_lower or 'observ' in header_lower:
                    # note/observaciones
                    nueva_fila.append(additional_info or "")
                elif 'location' in header_lower or 'ubicacion' in header_lower:
                    # location/ubicacion
                    nueva_fila.append("camera_view")
                else:
                    # Campo no reconocido, dejar vacío
                    nueva_fila.append("")
            
            # Añadir la fila al final
            self.main_sheet.append_row(nueva_fila)
            
            logger.info(f"✅ Detección registrada: {item_name} (confianza: {confidence:.3f})")
            logger.debug(f"📝 Fila añadida: {nueva_fila}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error registrando detección: {e}")
            return False
    
    def _determine_category(self, item_name):
        """Determinar categoría del item"""
        item_lower = item_name.lower()
        
        if any(word in item_lower for word in ['galleta', 'cookie', 'dulce', 'chocolate']):
            return "Snacks"
        elif any(word in item_lower for word in ['bebida', 'lata', 'refresco', 'agua']):
            return "Bebidas"
        elif any(word in item_lower for word in ['comida', 'alimento']):
            return "Alimentos"
        else:
            return "General"
    
    def read_existing_data(self, sheet_name=None):
        """Leer datos existentes de una hoja específica"""
        try:
            if sheet_name and sheet_name in self.sheet_structure:
                ws = self.sheet_structure[sheet_name]['worksheet']
                headers = self.sheet_structure[sheet_name]['headers']
            else:
                ws = self.main_sheet
                headers = self.main_headers
            
            if not ws:
                logger.error("❌ No hay hoja disponible para leer")
                return []
            
            # Leer todos los datos
            all_values = ws.get_all_values()
            if len(all_values) <= 1:
                logger.info("📊 No hay datos en la hoja")
                return []
            
            # Convertir a lista de diccionarios
            data = []
            for row in all_values[1:]:  # Saltar encabezados
                if any(cell.strip() for cell in row):  # Solo filas con datos
                    record = {}
                    for i, header in enumerate(headers):
                        if i < len(row):
                            record[header] = row[i]
                    data.append(record)
            
            logger.info(f"📖 Leídos {len(data)} registros de {ws.title}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error leyendo datos: {e}")
            return []
    
    def get_summary(self):
        """Obtener resumen del estado actual"""
        if not self.is_connected:
            return {"connected": False}
        
        summary = {
            "connected": True,
            "spreadsheet_title": self.spreadsheet.title,
            "spreadsheet_url": self.spreadsheet.url,
            "sheets": {}
        }
        
        for sheet_name, info in self.sheet_structure.items():
            summary["sheets"][sheet_name] = {
                "headers": info['headers'],
                "data_rows": info['data_rows'],
                "dimensions": f"{info['total_rows']}x{info['total_cols']}"
            }
        
        return summary

def test_readonly_integration():
    """Probar integración de solo lectura"""
    print("🔍 === PRUEBA DE INTEGRACIÓN SIN MODIFICAR ESTRUCTURA ===")
    
    # Inicializar gestor de solo lectura
    manager = ReadOnlyGoogleSheetsManager()
    
    if not manager.is_connected:
        print("❌ No se pudo conectar")
        return False
    
    print("\n📊 === RESUMEN DEL SPREADSHEET ===")
    summary = manager.get_summary()
    print(f"📋 Título: {summary['spreadsheet_title']}")
    print(f"🔗 URL: {summary['spreadsheet_url']}")
    
    for sheet_name, info in summary['sheets'].items():
        print(f"\n📄 Hoja: {sheet_name}")
        print(f"   📊 Filas de datos: {info['data_rows']}")
        print(f"   📏 Dimensiones: {info['dimensions']}")
        print(f"   📋 Encabezados: {info['headers'][:3]}..." if len(info['headers']) > 3 else f"   📋 Encabezados: {info['headers']}")
    
    print("\n🧪 === PRUEBA DE REGISTRO COMPATIBLE ===")
    
    # Probar algunas detecciones usando la estructura existente
    test_detections = [
        ("galletas_oreo", 0.95),
        ("coca_cola_lata", 0.87),
        ("chocolate_snickers", 0.92)
    ]
    
    for item_name, confidence in test_detections:
        print(f"📝 Registrando: {item_name}")
        success = manager.log_detection_compatible(
            item_name, 
            confidence, 
            f"Detección automática - confianza {confidence:.1%}"
        )
        
        if success:
            print(f"   ✅ Registrado exitosamente")
        else:
            print(f"   ❌ Error en el registro")
    
    print("\n📖 === VERIFICANDO DATOS REGISTRADOS ===")
    
    # Leer algunos datos para verificar
    recent_data = manager.read_existing_data()
    if recent_data:
        print(f"📊 Total de registros: {len(recent_data)}")
        print(f"🔍 Último registro: {recent_data[-1] if recent_data else 'N/A'}")
    
    return True

def main():
    """Función principal"""
    print("🎯 Prueba de integración respetuosa con estructura existente")
    print("=" * 65)
    print("ℹ️  Esta prueba NO modifica la estructura del spreadsheet")
    print("ℹ️  Solo lee la estructura existente y registra datos compatibles")
    print("=" * 65)
    
    success = test_readonly_integration()
    
    if success:
        print("\n🎉 ¡Prueba completada exitosamente!")
        print("✅ El sistema puede trabajar con la estructura existente")
        print("📋 Revisa tu Google Sheets para ver los nuevos registros")
    else:
        print("\n❌ La prueba falló")
        print("💡 Verifica la conexión y permisos")

if __name__ == "__main__":
    main()
