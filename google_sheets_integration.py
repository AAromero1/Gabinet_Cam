# Configuración para Google Sheets
# Archivo para manejar las credenciales y conexión a Google Sheets

import gspread
from google.oauth2.service_account import Credentials
import json
import os
import logging
from typing import Dict, List
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    """
    Gestor que respeta la estructura existente del spreadsheet
    sin modificar encabezados ni estructura establecida
    """
    
    def __init__(self, credentials_file: str = "calm-segment-credentials.json", 
                 spreadsheet_name: str = "Detecciones_Alimentos",
                 spreadsheet_id: str = None):
        """
        Inicializar el gestor de Google Sheets
        
        Args:
            credentials_file: Archivo JSON con las credenciales de la cuenta de servicio
            spreadsheet_name: Nombre del documento de Google Sheets (si no se usa ID)
            spreadsheet_id: ID específico del spreadsheet (extraído de URL)
        """
        self.credentials_file = credentials_file
        self.spreadsheet_name = spreadsheet_name
        self.spreadsheet_id = spreadsheet_id
        self.client = None
        self.sheet = None  # Hoja principal identificada automáticamente
        self.worksheet = None  # Mantener compatibilidad
        self.sheet_structure = {}  # Mapeo de estructura existente
        self.main_headers = []  # Encabezados de la hoja principal
        self.is_connected = False
        
        # Intentar conectar y analizar estructura
        self._connect()
    
    def _connect(self):
        """Conectar a Google Sheets y analizar estructura existente"""
        try:
            # Verificar si existe el archivo de credenciales
            if not os.path.exists(self.credentials_file):
                logger.warning(f"Archivo de credenciales no encontrado: {self.credentials_file}")
                logger.info("Creando archivo de credenciales de ejemplo...")
                self._create_credentials_template()
                return
            
            # Definir el scope necesario
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Cargar credenciales
            credentials = Credentials.from_service_account_file(
                self.credentials_file, scopes=scope
            )
            
            # Crear cliente
            self.client = gspread.authorize(credentials)
            
            # Intentar obtener el spreadsheet ID desde las credenciales si no se proporcionó
            if not self.spreadsheet_id:
                try:
                    with open(self.credentials_file, 'r') as f:
                        creds_data = json.load(f)
                        document_url = creds_data.get('document', '')
                        if '/spreadsheets/d/' in document_url:
                            self.spreadsheet_id = document_url.split('/spreadsheets/d/')[1].split('/')[0]
                            logger.info(f"📋 ID del spreadsheet extraído: {self.spreadsheet_id}")
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo extraer ID del spreadsheet: {e}")
            
            # Abrir spreadsheet usando ID o nombre
            try:
                if self.spreadsheet_id:
                    logger.info(f"🔗 Conectando al spreadsheet con ID: {self.spreadsheet_id}")
                    self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
                else:
                    logger.info(f"📝 Buscando spreadsheet por nombre: {self.spreadsheet_name}")
                    self.spreadsheet = self.client.open(self.spreadsheet_name)
            except gspread.SpreadsheetNotFound:
                if self.spreadsheet_id:
                    logger.error(f"❌ Spreadsheet con ID {self.spreadsheet_id} no encontrado o sin permisos")
                    logger.info("💡 Verifica que la cuenta de servicio tenga acceso al documento")
                    return
                else:
                    logger.info(f"Spreadsheet '{self.spreadsheet_name}' no encontrado. Creándolo...")
                    self.spreadsheet = self.client.create(self.spreadsheet_name)
                    self.spreadsheet.share('', perm_type='anyone', role='reader')
            
            # Analizar estructura existente sin modificarla
            self._analyze_existing_structure()
            
            self.is_connected = True
            logger.info("✅ Conectado exitosamente a Google Sheets")
            logger.info(f"📊 Spreadsheet: {self.spreadsheet.url}")
            
        except Exception as e:
            logger.error(f"❌ Error conectando a Google Sheets: {e}")
            self.is_connected = False
    
    def _create_credentials_template(self):
        """Crear un archivo de credenciales de ejemplo"""
        template = {
            "type": "service_account",
            "project_id": "tu-proyecto-id",
            "private_key_id": "tu-private-key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\nTU_PRIVATE_KEY_AQUI\n-----END PRIVATE KEY-----\n",
            "client_email": "tu-service-account@tu-proyecto.iam.gserviceaccount.com",
            "client_id": "tu-client-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/tu-service-account%40tu-proyecto.iam.gserviceaccount.com"
        }
        
        with open(self.credentials_file, 'w') as f:
            json.dump(template, f, indent=2)
        
        logger.info(f"📝 Archivo de credenciales de ejemplo creado: {self.credentials_file}")
        logger.info("🔧 Por favor, reemplaza los valores con tus credenciales reales de Google Cloud")
        logger.info("🌐 Instrucciones: https://docs.gspread.org/en/latest/oauth2.html")
    
    def _analyze_existing_structure(self):
        """Analizar y mapear la estructura existente sin cambiarla"""
        try:
            worksheets = self.spreadsheet.worksheets()
            logger.info(f"📊 Análisis de estructura: {len(worksheets)} hojas encontradas")
            
            for ws in worksheets:
                try:
                    headers = ws.row_values(1)
                    if headers:
                        # Contar filas con datos
                        all_values = ws.get_all_values()
                        data_rows = len([row for row in all_values[1:] if any(cell.strip() for cell in row)])
                        
                        # Guardar estructura para uso posterior
                        self.sheet_structure[ws.title] = {
                            'worksheet': ws,
                            'headers': headers,
                            'data_rows': data_rows,
                            'total_rows': ws.row_count,
                            'total_cols': ws.col_count
                        }
                        
                        logger.debug(f"📄 {ws.title}: {len(headers)} encabezados, {data_rows} filas de datos")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error analizando hoja {ws.title}: {e}")
            
            # Identificar hoja principal para detecciones
            self._identify_main_sheet()
                    
        except Exception as e:
            logger.error(f"❌ Error analizando estructura: {e}")
    
    def _identify_main_sheet(self):
        """Identificar cuál hoja usar para las detecciones"""
        self.sheet = None
        
        # Prioridad: Inventario > primera hoja con datos
        if 'Inventario' in self.sheet_structure:
            self.sheet = self.sheet_structure['Inventario']['worksheet']
            self.main_headers = self.sheet_structure['Inventario']['headers']
            self.worksheet = self.sheet  # Mantener compatibilidad
            logger.info(f"✅ Hoja principal identificada: Inventario")
        else:
            # Usar la primera hoja que tenga datos
            for sheet_name, info in self.sheet_structure.items():
                if info['data_rows'] >= 0:  # Cualquier hoja, incluso sin datos
                    self.sheet = info['worksheet']
                    self.main_headers = info['headers']
                    self.worksheet = self.sheet  # Mantener compatibilidad
                    logger.info(f"✅ Hoja principal identificada: {sheet_name}")
                    break
        
        if self.sheet:
            logger.info(f"📋 Encabezados detectados: {self.main_headers[:5]}..." if len(self.main_headers) > 5 else f"📋 Encabezados: {self.main_headers}")
        else:
            logger.error("❌ No se pudo identificar hoja principal")
    
    def _format_headers_for_sheet(self, sheet, num_cols):
        """Aplicar formato a los encabezados de una hoja específica"""
        try:
            # Generar rango dinámicamente
            end_col = chr(ord('A') + num_cols - 1)  # A, B, C, etc.
            range_str = f'A1:{end_col}1'
            
            sheet.format(range_str, {
                'textFormat': {'bold': True, 'fontSize': 10},
                'backgroundColor': {'red': 0.8, 'green': 0.9, 'blue': 1.0},
                'horizontalAlignment': 'CENTER',
                'borders': {
                    'top': {'style': 'SOLID'},
                    'bottom': {'style': 'SOLID'},
                    'left': {'style': 'SOLID'},
                    'right': {'style': 'SOLID'}
                }
            })
            
            # Congelar primera fila
            sheet.freeze(rows=1)
            
        except Exception as e:
            logger.error(f"❌ Error formateando encabezados de hoja específica: {e}")
    
    def log_detection(self, item_name, confidence, quantity=1, additional_info=None):
        """
        Registrar detección usando la estructura existente sin modificarla
        """
        if not self.sheet or not self.main_headers:
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
                    nueva_fila.append(str(quantity))
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
                elif 'last_seen' in header_lower:
                    # last_seen_at
                    nueva_fila.append(timestamp)
                elif 'last_event' in header_lower:
                    # last_event
                    nueva_fila.append("detection")
                else:
                    # Campo no reconocido, dejar vacío
                    nueva_fila.append("")
            
            # Añadir la fila al final
            self.sheet.append_row(nueva_fila)
            
            logger.info(f"✅ Detección registrada: {item_name} (confianza: {confidence:.3f})")
            logger.debug(f"📝 Fila añadida con {len(nueva_fila)} campos")
            
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
                ws = self.sheet
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
            
            logger.info(f"📊 Leídos {len(data)} registros de {ws.title}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error leyendo datos: {e}")
            return []
    
    def remove_item_from_inventory(self, item_id, reason="manual_removal"):
        """
        Eliminar un item del inventario por su ID
        
        Args:
            item_id: ID del item a eliminar
            reason: Razón de la eliminación
        """
        if not self.sheet:
            logger.error("❌ No hay hoja principal disponible")
            return False
        
        try:
            # Buscar la fila del item
            all_values = self.sheet.get_all_values()
            
            for i, row in enumerate(all_values[1:], start=2):  # Empezar desde fila 2 (saltar encabezados)
                if len(row) > 0 and row[0] == item_id:  # Asumir que item_id está en la primera columna
                    # Eliminar la fila
                    self.sheet.delete_rows(i)
                    logger.info(f"✅ Item eliminado del inventario: {item_id} (razón: {reason})")
                    return True
            
            logger.warning(f"⚠️ Item no encontrado en inventario: {item_id}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error eliminando item del inventario: {e}")
            return False
    
    def log_removal_to_bitacora(self, item_id, item_name, reason="manual_removal"):
        """
        Registrar la eliminación en la hoja de bitácora
        
        Args:
            item_id: ID del item eliminado
            item_name: Nombre del item eliminado
            reason: Razón de la eliminación
        """
        try:
            # Obtener o crear hoja de bitácora
            bitacora_sheet = None
            try:
                bitacora_sheet = self.spreadsheet.worksheet("Bitacora")
            except:
                # Crear hoja de bitácora si no existe
                bitacora_sheet = self.spreadsheet.add_worksheet(title="Bitacora", rows="100", cols="9")
                headers_bitacora = [
                    'timestamp', 'item_id', 'name', 'delta_qty', 'new_qty', 
                    'event', 'source', 'payload_id', 'note'
                ]
                bitacora_sheet.append_row(headers_bitacora)
                self._format_headers_for_sheet(bitacora_sheet, len(headers_bitacora))
            
            if bitacora_sheet:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                bitacora_row = [
                    timestamp,
                    item_id,
                    item_name,
                    "-1",  # delta_qty (eliminación)
                    "0",   # new_qty (ya no está)
                    "removed",  # event
                    "system",  # source
                    f"REM_{int(time.time())}",  # payload_id
                    f"Item eliminado: {reason}"  # note
                ]
                
                bitacora_sheet.append_row(bitacora_row)
                logger.info(f"✅ Eliminación registrada en bitácora: {item_name}")
                return True
            
        except Exception as e:
            logger.error(f"❌ Error registrando eliminación en bitácora: {e}")
            return False
    
    def add_synonym(self, term, item_id, category=None):
        """
        Agregar un sinónimo a la hoja de sinónimos
        
        Args:
            term: Término sinónimo
            item_id: ID del item relacionado
            category: Categoría (opcional)
        """
        try:
            # Obtener o crear hoja de sinónimos
            sinonimos_sheet = None
            try:
                sinonimos_sheet = self.spreadsheet.worksheet("Sinonimos")
            except:
                # Crear hoja de sinónimos si no existe
                sinonimos_sheet = self.spreadsheet.add_worksheet(title="Sinonimos", rows="100", cols="3")
                headers_sinonimos = ['term', 'item_id', 'category']
                sinonimos_sheet.append_row(headers_sinonimos)
                self._format_headers_for_sheet(sinonimos_sheet, len(headers_sinonimos))
            
            if sinonimos_sheet:
                # Verificar si ya existe el sinónimo
                existing_data = sinonimos_sheet.get_all_values()
                for row in existing_data[1:]:  # Saltar encabezados
                    if len(row) >= 2 and row[0].lower() == term.lower() and row[1] == item_id:
                        logger.info(f"📝 Sinónimo ya existe: {term} -> {item_id}")
                        return True
                
                # Agregar nuevo sinónimo
                new_row = [term, item_id]
                if category:
                    new_row.append(category)
                
                sinonimos_sheet.append_row(new_row)
                logger.info(f"✅ Sinónimo agregado: {term} -> {item_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error agregando sinónimo: {e}")
            return False
    
    def get_last_item_id(self):
        """
        Obtener el ID del último item agregado al inventario
        """
        try:
            data = self.read_existing_data()
            if data and len(data) > 0:
                return data[-1].get('item_id', None)
            return None
        except Exception as e:
            logger.error(f"❌ Error obteniendo último item ID: {e}")
            return None
    
    def update_item_quantity(self, item_id, new_quantity, additional_info=None):
        """
        Actualizar la cantidad de un item existente por su ID
        """
        if not self.sheet or not self.main_headers:
            logger.error("❌ No hay hoja principal disponible")
            return False
        
        try:
            # Obtener todos los datos
            all_data = self.sheet.get_all_values()
            if not all_data:
                logger.error("❌ No hay datos en la hoja")
                return False
            
            headers = all_data[0]
            
            # Encontrar índices de columnas importantes
            item_id_col = None
            quantity_col = None
            updated_col = None
            
            for i, header in enumerate(headers):
                header_lower = header.lower()
                if 'id' in header_lower and 'item' in header_lower:
                    item_id_col = i
                elif 'quantity' in header_lower or 'cantidad' in header_lower:
                    quantity_col = i
                elif 'updated' in header_lower or 'actualizado' in header_lower:
                    updated_col = i
            
            if item_id_col is None:
                logger.error("❌ No se encontró columna de item_id")
                return False
            
            # Buscar la fila con el item_id
            row_to_update = None
            for i, row in enumerate(all_data[1:], start=2):  # start=2 porque enumerate empieza en 0 pero las filas de gsheets empiezan en 1
                if len(row) > item_id_col and row[item_id_col] == item_id:
                    row_to_update = i
                    break
            
            if row_to_update is None:
                logger.error(f"❌ No se encontró item con ID: {item_id}")
                return False
            
            # Actualizar cantidad
            if quantity_col is not None:
                self.sheet.update_cell(row_to_update, quantity_col + 1, str(new_quantity))
                logger.info(f"✅ Cantidad actualizada para {item_id}: {new_quantity}")
            
            # Actualizar timestamp de modificación si existe la columna
            if updated_col is not None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.sheet.update_cell(row_to_update, updated_col + 1, timestamp)
            
            # Si hay información adicional y columna para notas
            if additional_info:
                for i, header in enumerate(headers):
                    if 'note' in header.lower() or 'nota' in header.lower() or 'info' in header.lower():
                        current_info = all_data[row_to_update - 1][i] if len(all_data[row_to_update - 1]) > i else ""
                        new_info = f"{current_info}; {additional_info}" if current_info else additional_info
                        self.sheet.update_cell(row_to_update, i + 1, new_info)
                        break
            
            time.sleep(1)  # Pausa para evitar rate limiting
            return True
            
        except Exception as e:
            logger.error(f"❌ Error actualizando cantidad del item {item_id}: {e}")
            return False
