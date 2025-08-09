# RUTA: app/infrastructure/persistence/sqlserver_repository.py

from app.database.connector import get_db_read, get_db_write
from app.domain.models.usuario import Usuario
from app.domain.models.personal import Personal
from app.domain.repositories.i_usuario_repository import IUsuarioRepository
from app.domain.repositories.i_personal_repository import IPersonalRepository
from app.domain.repositories.i_auditoria_repository import IAuditoriaRepository
from app.utils.pagination import SimplePagination

def _row_to_dict(cursor, row):
    if not row: return None
    return dict(zip([column[0] for column in cursor.description], row))

class SqlServerUsuarioRepository(IUsuarioRepository):
    def find_by_id(self, user_id):
        conn = get_db_read()
        cursor = conn.cursor()
        # El SP sp_obtener_usuario_por_id ya trae el nombre y el último login.
        query = "{CALL sp_obtener_usuario_por_id(?)}"
        cursor.execute(query, user_id)
        row_dict = _row_to_dict(cursor, cursor.fetchone())
        return Usuario.from_dict(row_dict)

    def find_by_username_with_email(self, username):
        conn = get_db_read()
        cursor = conn.cursor()
        # El SP sp_obtener_usuario_por_username ya trae el nombre y el último login.
        query = "{CALL sp_obtener_usuario_por_username(?)}"
        cursor.execute(query, username)
        row_dict = _row_to_dict(cursor, cursor.fetchone())
        return Usuario.from_dict(row_dict)

    def set_2fa_code(self, user_id, hashed_code, expiry_date):
        conn = get_db_write()
        cursor = conn.cursor()
        query = "UPDATE usuarios SET two_factor_code = ?, two_factor_expiry = ? WHERE id_usuario = ?"
        cursor.execute(query, hashed_code, expiry_date, user_id)
        conn.commit()

    def clear_2fa_code(self, user_id):
        conn = get_db_write()
        cursor = conn.cursor()
        query = "UPDATE usuarios SET two_factor_code = NULL, two_factor_expiry = NULL WHERE id_usuario = ?"
        cursor.execute(query, user_id)
        conn.commit()

    def update_password_hash(self, username, new_hash):
        conn = get_db_write()
        cursor = conn.cursor()
        cursor.execute("{CALL sp_actualizar_password_usuario(?, ?)}", username, new_hash)
        conn.commit()    

    def update_last_login(self, user_id):
        """Llama a un SP para actualizar la fecha del último login."""
        conn = get_db_write()
        cursor = conn.cursor()
        # Este nuevo SP simplemente actualizará el campo 'ultimo_login' a la fecha actual.
        cursor.execute("{CALL sp_actualizar_ultimo_login(?)}", user_id)
        conn.commit()

# --- REPOSITORIO DE PERSONAL ---
# Implementación completa del repositorio de personal.
class SqlServerPersonalRepository(IPersonalRepository):
    def find_document_by_id(self, document_id):
        """
        Llama al SP para obtener los datos de un único documento por su ID.
        """
        conn = get_db_read()
        cursor = conn.cursor()
        cursor.execute("{CALL sp_obtener_documento_por_id(?)}", document_id)
        # fetchone() recupera la única fila que devuelve el SP
        return cursor.fetchone()

    def delete_document_by_id(self, document_id):
        """
        Llama al SP para la eliminación lógica de un documento.
        """
        conn = get_db_write()
        cursor = conn.cursor()
        cursor.execute("{CALL sp_eliminar_documento_logico(?)}", document_id)
        conn.commit()


    def find_tipos_documento_by_seccion(self, id_seccion):
        """
        Llama a un procedimiento almacenado para obtener los tipos de documento 
        asociados a una sección.
        """
        conn = get_db_read()
        cursor = conn.cursor()
        
        # --- LA CORRECCIÓN CLAVE: LLAMAR AL SP ---
        cursor.execute("{CALL sp_listar_tipos_documento_por_seccion(?)}", id_seccion)
        
        # Devuelve una lista de diccionarios, ideal para ser convertida a JSON
        return [{"id": row.id_tipo, "nombre": row.nombre_tipo} for row in cursor.fetchall()]


    # Llama a un SP para obtener la lista de documentos de un empleado.
    def find_documents_by_personal_id(self, personal_id):
        conn = get_db_read()
        cursor = conn.cursor()
        # Este SP debe devolver la lista de documentos para un id_personal.
        cursor.execute("{CALL sp_listar_documentos_por_personal(?)}", personal_id)
        # Se asume que el SP devuelve filas que se pueden mapear al modelo Documento.
        return [_row_to_dict(cursor, row) for row in cursor.fetchall()]

    def get_full_legajo_by_id(self, personal_id):
        conn = get_db_read()
        cursor = conn.cursor()
        cursor.execute("{CALL sp_obtener_legajo_completo_por_personal(?)}", personal_id)
        
        # El primer resultado es la información del personal.
        personal_info = _row_to_dict(cursor, cursor.fetchone())
        if not personal_info:
            return None # Si no hay datos personales, el legajo no existe.

        legajo = {"personal": personal_info}
        
        # Se procesan los siguientes conjuntos de resultados.
        if cursor.nextset(): legajo["estudios"] = [_row_to_dict(cursor, row) for row in cursor.fetchall()]
        if cursor.nextset(): legajo["capacitaciones"] = [_row_to_dict(cursor, row) for row in cursor.fetchall()]
        if cursor.nextset(): legajo["contratos"] = [_row_to_dict(cursor, row) for row in cursor.fetchall()]
        if cursor.nextset(): legajo["historial_laboral"] = [_row_to_dict(cursor, row) for row in cursor.fetchall()]
        if cursor.nextset(): legajo["licencias"] = [_row_to_dict(cursor, row) for row in cursor.fetchall()]
        if cursor.nextset(): legajo["documentos"] = [_row_to_dict(cursor, row) for row in cursor.fetchall()]
            
        return legajo
    
    # Llama a un SP para listar, filtrar y paginar al personal.
    def get_all_paginated(self, page, per_page, filters):
        conn = get_db_read()
        cursor = conn.cursor()
        dni_filter = filters.get('dni') if filters else None
        nombres_filter = filters.get('nombres') if filters else None
        
        cursor.execute("{CALL sp_listar_personal_paginado(?, ?, ?, ?)}", page, per_page, dni_filter, nombres_filter)
        results = [_row_to_dict(cursor, row) for row in cursor.fetchall()]
        
        cursor.nextset()
        total = cursor.fetchone()[0]
        return SimplePagination(results, page, per_page, total)

    # Llama a un SP para crear un nuevo registro de personal.
    def create(self, form_data):
        conn = get_db_write()
        cursor = conn.cursor()
        params = (form_data.get('dni'), form_data.get('nombres'), form_data.get('apellidos'), form_data.get('sexo'),
                  form_data.get('fecha_nacimiento'), form_data.get('direccion'), form_data.get('telefono'),
                  form_data.get('email'), form_data.get('estado_civil'), form_data.get('nacionalidad'),
                  form_data.get('id_unidad'), form_data.get('fecha_ingreso'))
        cursor.execute("{CALL sp_registrar_personal(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)}", params)
        new_id = cursor.fetchone()[0]
        conn.commit()
        return new_id
    
    # Llama a un SP para añadir un documento.
    def add_document(self, doc_data, file_bytes):
        conn = get_db_write()
        cursor = conn.cursor()
        params = (doc_data.get('id_personal'), doc_data.get('id_tipo'), doc_data.get('id_seccion'),
                  doc_data.get('nombre_archivo'), doc_data.get('fecha_emision'), doc_data.get('fecha_vencimiento'),
                  doc_data.get('descripcion'), file_bytes, doc_data.get('hash_archivo'))
        cursor.execute("{CALL sp_subir_documento(?, ?, ?, ?, ?, ?, ?, ?, ?)}", params)
        conn.commit()
    
    # Métodos para obtener listas para los formularios SelectField.
    def get_unidades_for_select(self):
        conn = get_db_read()
        cursor = conn.cursor()
        cursor.execute("SELECT id_unidad, nombre FROM unidad_administrativa ORDER BY nombre")
        return [(row.id_unidad, row.nombre) for row in cursor.fetchall()]

    def get_secciones_for_select(self):
        conn = get_db_read()
        cursor = conn.cursor()
        cursor.execute("SELECT id_seccion, nombre_seccion FROM legajo_secciones ORDER BY id_seccion")
        return [(row.id_seccion, row.nombre_seccion) for row in cursor.fetchall()]

    def get_tipos_documento_by_seccion(self, seccion_id):
        conn = get_db_read()
        cursor = conn.cursor()
        cursor.execute("{CALL sp_listar_tipos_documento_por_seccion(?)}", seccion_id)
        return [(row.id_tipo, row.nombre_tipo) for row in cursor.fetchall()]


    def get_tipos_documento_for_select(self):
        conn = get_db_read()
        cursor = conn.cursor()
        cursor.execute("SELECT id_tipo, nombre_tipo FROM tipo_documento ORDER BY nombre_tipo")
        return [(row.id_tipo, row.nombre_tipo) for row in cursor.fetchall()]

    # Implementación del método de actualización.
    def update(self, personal_id, form_data):
        conn = get_db_write()
        cursor = conn.cursor()
        # Llama a un SP para actualizar los datos del personal.
        # El SP debe estar preparado para recibir todos los campos del formulario.
        params = (
            personal_id,
            form_data.get('dni'),
            form_data.get('nombres'),
            form_data.get('apellidos'),
            form_data.get('sexo'),
            form_data.get('fecha_nacimiento'),
            form_data.get('direccion'),
            form_data.get('telefono'),
            form_data.get('email'),
            form_data.get('estado_civil'),
            form_data.get('nacionalidad'),
            form_data.get('id_unidad'),
            form_data.get('fecha_ingreso')
        )
        cursor.execute("{CALL sp_actualizar_personal(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)}", params)
        conn.commit()


    # Llama a un SP para obtener todos los datos necesarios para el reporte general.
    def get_all_for_report(self):
        conn = get_db_read()
        cursor = conn.cursor()
        cursor.execute("{CALL sp_generar_reporte_general_personal}")
        return [_row_to_dict(cursor, row) for row in cursor.fetchall()]    
    # Llama al SP para el borrado suave (desactivación) de un empleado.
    def delete_by_id(self, personal_id):
        conn = get_db_write()
        cursor = conn.cursor()
        cursor.execute("{CALL sp_eliminar_personal(?)}", personal_id)
        conn.commit()
        
    def find_by_id(self, personal_id):
        conn = get_db_read()
        cursor = conn.cursor()
        cursor.execute("{CALL sp_obtener_personal_por_id(?)}", personal_id)
        row = cursor.fetchone()
        return Personal.from_dict(_row_to_dict(cursor, row)) if row else None


# --- REPOSITORIO DE AUDITORÍA ---
# Implementación completa y corregida del repositorio de auditoría.
class SqlServerAuditoriaRepository(IAuditoriaRepository):
    # Llama a un SP para registrar un evento en la bitácora.
    def log_event(self, id_usuario, modulo, accion, descripcion, detalle_json=None):
        conn = get_db_write()
        cursor = conn.cursor()
        cursor.execute("{CALL sp_registrar_bitacora(?, ?, ?, ?, ?)}", id_usuario, modulo, accion, descripcion, detalle_json)
        conn.commit()

    # Obtiene los logs de forma paginada.
    def get_all_logs_paginated(self, page, per_page):
        conn = get_db_read()
        cursor = conn.cursor()
        # Llama a un SP que maneja la paginación de la tabla bitacora.
        cursor.execute("{CALL sp_listar_bitacora_paginada(?, ?)}", page, per_page)
        # Procesa los resultados.
        results = [_row_to_dict(cursor, row) for row in cursor.fetchall()]
        # Obtiene el total de registros para los controles de paginación.
        cursor.nextset()
        total = cursor.fetchone()[0]
        return SimplePagination(results, page, per_page, total)