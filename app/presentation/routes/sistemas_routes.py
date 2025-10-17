# RUTA: app/presentation/routes/sistemas_routes.py

from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from app.decorators import role_required # Asumimos que este decorador verifica el rol
from app.application.forms import UserManagementForm # Asumimos un formulario para la gestión de usuarios
import io
from datetime import datetime

# --- IMPORTACIÓN ADICIONAL PARA LA NUEVA FUNCIONALIDAD ---
# Importamos el repositorio que puede hablar con la base de datos para los errores
from app.infrastructure.persistence.sqlserver_repository import SqlServerBackupRepository

# Blueprint para las funcionalidades exclusivas del rol de Sistemas.
sistemas_bp = Blueprint('sistemas', __name__) 

# ------------------------------------------------------------------------
# 1. VISTAS PRINCIPALES DEL DASHBOARD
# ------------------------------------------------------------------------

@sistemas_bp.route('/dashboard')
@login_required
@role_required('Sistemas')
def dashboard():
    """
    Controlador principal del Dashboard de Sistemas. 
    Muestra la vista VISUAL con tarjetas de acceso y monitoreo.
    """
    return render_template('sistemas/sistemas_inicio.html') 


@sistemas_bp.route('/auditoria')
@login_required
@role_required('Sistemas')
def auditoria():
    """
    Vista de Auditoría: Muestra la tabla de logs (el 'puro texto').
    """
    page = request.args.get('page', 1, type=int)
    audit_service = current_app.config['AUDIT_SERVICE']
    pagination = audit_service.get_logs(page, 20)
    audit_service.log(current_user.id, 'Auditoria', 'CONSULTA', f'El usuario consultó la página {page} de la bitácora.')
    return render_template('sistemas/auditoria.html', pagination=pagination)


# ------------------------------------------------------------------------
# 2. GESTIÓN DE USUARIOS (Desde la tarjeta 'Gestión de Roles y Usuarios')
# ------------------------------------------------------------------------

@sistemas_bp.route('/usuarios')
@login_required
@role_required('Sistemas')
def gestionar_usuarios():
    """
    Muestra el listado y el control de usuarios del sistema (CRUD).
    """
    usuario_service = current_app.config['USUARIO_SERVICE']
    usuarios = usuario_service.get_all_users_with_roles() 
    return render_template('sistemas/gestionar_usuarios.html', usuarios=usuarios)


@sistemas_bp.route('/usuarios/crear', methods=['GET', 'POST'])
@login_required
@role_required('Sistemas')
def crear_usuario():
    form = UserManagementForm() 
    if form.validate_on_submit():
        try:
            usuario_service = current_app.config['USUARIO_SERVICE']
            usuario_service.create_user(form.data)
            flash('Usuario creado con éxito.', 'success')
            return redirect(url_for('sistemas.gestionar_usuarios'))
        except Exception as e:
            flash(f'Error al crear usuario: {e}', 'danger')
    return render_template('sistemas/crear_usuario.html', form=form)


@sistemas_bp.route('/usuarios/editar/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required('Sistemas')
def editar_usuario(user_id):
    print("--- DEBUG: INTENTANDO ACCEDER A LA FUNCIÓN EDITAR_USUARIO ---")
    import traceback
    try:
        usuario_service = current_app.config['USUARIO_SERVICE']
        user = usuario_service.get_user_by_id(user_id)
        if not user:
            flash('Usuario no encontrado.', 'danger')
            return redirect(url_for('sistemas.gestionar_usuarios'))
        
        form = UserManagementForm(obj=user)
        
        # Lógica para poblar los roles en el formulario
        # Asumimos que el servicio puede proveer una lista de roles
        # roles = usuario_service.get_all_roles() 
        # form.id_rol.choices = [(r.id, r.nombre) for r in roles]

        if form.validate_on_submit():
            usuario_service.update_user(user_id, form.data)
            flash('Usuario actualizado con éxito.', 'success')
            return redirect(url_for('sistemas.gestionar_usuarios'))
        
        return render_template('sistemas/editar_usuario.html', form=form, user=user)

    except Exception as e:
        # Bloque de depuración para forzar la visibilidad del error
        error_trace = traceback.format_exc()
        current_app.logger.error(f"ERROR CRÍTICO EN EDITAR_USUARIO: {e}\n{error_trace}")
        print(f"!!!!!!!!!!!!!! ERROR DETECTADO EN EDITAR_USUARIO !!!!!!!!!!!!!!")
        print(error_trace)
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        flash(f"Ocurrió un error grave al cargar la página de edición. Revise la terminal.", 'danger')
        return redirect(url_for('sistemas.gestionar_usuarios'))


@sistemas_bp.route('/usuarios/reset_password/<int:user_id>', methods=['POST'])
@login_required
@role_required('Sistemas')
def reset_password(user_id):
    try:
        usuario_service = current_app.config['USUARIO_SERVICE']
        usuario_service.reset_user_password(user_id) 
        flash('Contraseña reseteada con éxito. El usuario deberá cambiarla al iniciar sesión.', 'success')
    except Exception as e:
        current_app.logger.error(f"Error al resetear contraseña del usuario {user_id}: {e}")
        flash('Ocurrió un error técnico al resetear la contraseña.', 'danger')
    return redirect(url_for('sistemas.gestionar_usuarios'))


# ------------------------------------------------------------------------
# 3. MANTENIMIENTO TÉCNICO Y BACKUPS (Desde la tarjeta 'Monitoreo')
# ------------------------------------------------------------------------

@sistemas_bp.route('/mantenimiento/backups')
@login_required
@role_required('Sistemas')
def gestion_backups():
    try:
        backup_service = current_app.config['BACKUP_SERVICE']
        historial_data = backup_service.get_backup_history() 
    except Exception as e:
        current_app.logger.error(f"Error al cargar historial de backups: {e}")
        historial_data = []
    return render_template('sistemas/gestion_backups.html', historial=historial_data) 

@sistemas_bp.route('/mantenimiento/run_backup', methods=['POST'])
@login_required
@role_required('Sistemas')
def run_backup():
    try:
        if 'BACKUP_SERVICE' not in current_app.config:
            raise Exception("El servicio de backup no está inicializado.")
        current_app.config['BACKUP_SERVICE'].execute_full_backup()
        flash('Copia de seguridad iniciada y completada con éxito.', 'success')
    except Exception as e:
        current_app.logger.error(f"Error al ejecutar backup manual: {e}")
        flash(f'Error al ejecutar la copia de seguridad. Detalle: {e}', 'danger')
    return redirect(url_for('sistemas.gestion_backups'))


@sistemas_bp.route('/mantenimiento/estado_servidor')
@login_required
@role_required('Sistemas')
def estado_servidor():
    return render_template('sistemas/estado_servidor.html')

# --- MODIFICACIÓN: RUTA DE ERRORES CON LÓGICA REAL ---
@sistemas_bp.route('/errores')
@login_required
@role_required('Sistemas')
def errores():
    """
    Vista para ver el registro de errores. Ahora obtiene los datos reales de la BD.
    """
    try:
        # 1. Crea una instancia del repositorio para hablar con la BD
        repo = SqlServerBackupRepository()
        # 2. Llama a la función para obtener la lista de errores
        lista_de_errores = repo.obtener_historial_errores()
        # 3. Pasa la lista a la plantilla HTML
        return render_template('sistemas/registro_errores.html', errores=lista_de_errores)
    except Exception as e:
        # Si algo falla al obtener los errores, muestra un mensaje
        current_app.logger.error(f"No se pudo cargar el historial de errores: {e}")
        flash(f"No se pudo cargar el historial de errores: {e}", "danger")
        return render_template('sistemas/registro_errores.html', errores=[])

# --- NUEVA RUTA PARA GENERAR UN ERROR DE PRUEBA ---
@sistemas_bp.route('/test-error')
@login_required
@role_required('Sistemas')
def generar_error_prueba():
    """
    Visita esta URL para forzar un error y que se guarde en la bitácora.
    """
    repo = SqlServerBackupRepository()
    try:
        # Forzamos un error común (división por cero) para probar
        resultado = 1 / 0
    except Exception as e:
        # Obtenemos el ID del usuario actual para registrar quién causó el error
        usuario_id = current_user.id if current_user.is_authenticated else None
        
        # Usamos la función del repositorio para registrar el error en la base de datos
        repo.registrar_error(
            modulo='sistemas.test_error', 
            descripcion=f"Error de prueba forzado: {str(e)}", 
            usuario_id=usuario_id
        )
        flash('Se ha generado y registrado un error de prueba en la bitácora.', 'info')
        
    # Redirigimos de vuelta a la página de errores para ver el resultado
    return redirect(url_for('sistemas.errores'))


# ------------------------------------------------------------------------
# 4. REPORTES TÉCNICOS/AVANZADOS
# ------------------------------------------------------------------------

@sistemas_bp.route('/reportes')
@login_required
@role_required('Sistemas')
def reportes():
    return render_template('sistemas/reportes.html')


# ------------------------------------------------------------------------
# 5. SOLICITUDES PENDIENTES
# ------------------------------------------------------------------------

@sistemas_bp.route('/solicitudes')
@login_required
@role_required('Sistemas')
def solicitudes_pendientes():
    solicitudes_service = current_app.config.get('SOLICITUDES_SERVICE')
    solicitudes = solicitudes_service.get_all_pending() if solicitudes_service else []
    return render_template('sistemas/solicitudes_pendientes.html', requests=solicitudes)


@sistemas_bp.route('/solicitudes/procesar/<int:request_id>', methods=['POST'])
@login_required
@role_required('Sistemas')
def procesar_solicitud(request_id):
    action = request.form.get('action') # 'aprobar' o 'rechazar'
    if action in ['aprobar', 'rechazar']:
        solicitud_service = current_app.config['SOLICITUDES_SERVICE']
        solicitud_service.process_request(request_id, action)
        flash(f'Solicitud {action}da con éxito.', 'success')
    else:
        flash('Acción no válida.', 'danger')
    return redirect(url_for('sistemas.solicitudes_pendientes'))

