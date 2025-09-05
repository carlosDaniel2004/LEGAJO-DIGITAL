# RUTA: app/presentation/routes/legajo_routes.py

import io
import mimetypes
import pyodbc
from flask import Blueprint, jsonify, render_template, redirect, send_file, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.decorators import role_required
from app.application.forms import PersonalForm, DocumentoForm, FiltroPersonalForm

legajo_bp = Blueprint('legajo', __name__)

# --- NUEVA RUTA API para obtener tipos de documento por sección ---
@legajo_bp.route('/api/tipos_documento/por_seccion/<int:seccion_id>', methods=['GET'])
@login_required
@role_required('AdministradorLegajos', 'RRHH', 'Sistemas') # Ajusta los roles si es necesario
def get_tipos_documento_by_seccion(seccion_id):
    legajo_service = current_app.config['LEGAJO_SERVICE']
    tipos_documento = legajo_service.get_tipos_documento_by_seccion(seccion_id)
    # Formatea la respuesta para que sea fácil de consumir por JavaScript
    return jsonify([{'id': id, 'nombre': nombre} for id, nombre in tipos_documento])

@legajo_bp.route('/dashboard')
@login_required
@role_required('AdministradorLegajos', 'RRHH')
def dashboard():
    return render_template('admin/dashboard.html', username=current_user.username)

@legajo_bp.route('/personal/<int:personal_id>')
@login_required
@role_required('AdministradorLegajos', 'RRHH', 'Sistemas')
def ver_legajo(personal_id):
    legajo_service = current_app.config['LEGAJO_SERVICE']
    legajo_completo = legajo_service.get_personal_details(personal_id)
    
    if not legajo_completo or not legajo_completo.get('personal'):
        flash('El legajo solicitado no existe.', 'danger')
        return redirect(url_for('legajo.listar_personal'))
        
    form_documento = DocumentoForm()
    form_documento.id_seccion.choices = [('0', '-- Seleccione Sección --')] + legajo_service.get_secciones_for_select()
    form_documento.id_tipo.choices = [('0', '-- Seleccione Tipo --')] + legajo_service.get_tipos_documento_for_select()
    
    # Se añade 'legajo_service=legajo_service' para que la plantilla pueda usarlo.
    return render_template(
        'admin/ver_legajo_completo.html', 
        legajo=legajo_completo, 
        form_documento=form_documento,
        legajo_service=legajo_service
    )


@legajo_bp.route('/personal')
@login_required
@role_required('AdministradorLegajos', 'RRHH', 'Sistemas')
def listar_personal():
    form = FiltroPersonalForm(request.args)
    page = request.args.get('page', 1, type=int)
    filters = {'dni': form.dni.data, 'nombres': form.nombres.data}
    legajo_service = current_app.config['LEGAJO_SERVICE']
    pagination = legajo_service.get_all_personal_paginated(page, 15, filters)
    return render_template('admin/listar_personal.html', form=form, pagination=pagination)

@legajo_bp.route('/personal/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('AdministradorLegajos')
def crear_personal():
    form = PersonalForm()
    legajo_service = current_app.config['LEGAJO_SERVICE']
    form.id_unidad.choices = [('0', '-- Seleccione Unidad --')] + legajo_service.get_unidades_for_select()
    
    if form.validate_on_submit():
        try:
            legajo_service.register_new_personal(form.data, current_user.id)
            flash('Legajo creado exitosamente.', 'success')
            return redirect(url_for('legajo.listar_personal'))
        except pyodbc.Error as db_err:
            err_msg = str(db_err)
            current_app.logger.error(f"Error de base de datos al crear legajo: {err_msg}")
            if 'DNI ya se encuentra registrado' in err_msg:
                flash('Error al crear el legajo: El DNI ingresado ya existe.', 'danger')
            elif 'correo electrónico ya está en uso' in err_msg:
                flash('Error al crear el legajo: El correo electrónico ingresado ya está en uso.', 'danger')
            else:
                flash('Ocurrió un error en la base de datos al intentar crear el legajo.', 'danger')
        except Exception as e:
            current_app.logger.error(f"Error inesperado al crear legajo: {e}")
            flash('Ocurrió un error inesperado al procesar su solicitud.', 'danger')
            
    return render_template('admin/crear_personal.html', form=form, titulo="Crear Nuevo Legajo")


@legajo_bp.route('/personal/<int:personal_id>/documento/subir', methods=['POST'])
@login_required
@role_required('AdministradorLegajos')
def subir_documento(personal_id):
    form = DocumentoForm()
    legajo_service = current_app.config['LEGAJO_SERVICE']
    form.id_seccion.choices = [('0', '-- Seleccione Sección --')] + legajo_service.get_secciones_for_select()
    form.id_tipo.choices = [('0', '-- Seleccione Tipo --')] + legajo_service.get_tipos_documento_for_select()
    
    if form.validate_on_submit():
        try:
            form_data = form.data
            form_data['id_personal'] = personal_id
            legajo_service.upload_document_to_personal(form_data, form.archivo.data, current_user.id)
            flash('Documento subido correctamente.', 'success')
        except Exception as e:
            current_app.logger.error(f"Error al subir documento para personal {personal_id}: {e}")
            flash(f'Ocurrió un error al subir el documento: {e}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error en el campo '{getattr(form, field).label.text}': {error}", 'danger')
                break
    return redirect(url_for('legajo.ver_legajo', personal_id=personal_id))

@legajo_bp.route('/personal/<int:personal_id>/eliminar', methods=['POST'])
@login_required
@role_required('AdministradorLegajos')
def eliminar_personal(personal_id):
    try:
        legajo_service = current_app.config['LEGAJO_SERVICE']
        legajo_service.delete_personal_by_id(personal_id, current_user.id)
        flash('El legajo ha sido desactivado correctamente.', 'success')
    except Exception as e:
        current_app.logger.error(f"Error al eliminar legajo {personal_id}: {e}")
        flash(f'Ocurrió un error al desactivar el legajo: {e}', 'danger')
    return redirect(url_for('legajo.listar_personal'))

@legajo_bp.route('/personal/<int:personal_id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('AdministradorLegajos')
def editar_personal(personal_id):
    legajo_service = current_app.config['LEGAJO_SERVICE']
    
    legajo_data = legajo_service.get_personal_details(personal_id)
    if not legajo_data or not legajo_data.get('personal'):
        flash('El legajo que intenta editar no existe.', 'danger')
        return redirect(url_for('legajo.listar_personal'))

    persona_data = legajo_data['personal']
    
    form = PersonalForm(data=persona_data)
    form.id_unidad.choices = [('0', '-- Seleccione Unidad --')] + legajo_service.get_unidades_for_select()
    
    if request.method == 'GET':
        form.id_unidad.data = persona_data.get('id_unidad')

    if form.validate_on_submit():
        try:
            # legajo_service.update_personal_details(personal_id, form.data, current_user.id)
            flash('Legajo actualizado exitosamente.', 'success')
            return redirect(url_for('legajo.ver_legajo', personal_id=personal_id))
        except Exception as e:
            current_app.logger.error(f"Error al actualizar legajo {personal_id}: {e}")
            flash('Ocurrió un error al actualizar el legajo.', 'danger')
            
    return render_template('admin/editar_personal.html', form=form, persona=persona_data, titulo="Editar Legajo")



@legajo_bp.route('/documento/<int:documento_id>/ver')
@login_required
@role_required('AdministradorLegajos', 'RRHH', 'Sistemas')
def ver_documento(documento_id):
    """
    Gestiona la solicitud para ver un archivo en una nueva pestaña.
    Obtiene el archivo desde el servicio y lo envía al navegador para ser mostrado.
    """
    legajo_service = current_app.config['LEGAJO_SERVICE']
    try:
        document = legajo_service.get_document_for_download(documento_id)
        
        if not document or not document.get('data'):
            flash('El documento no fue encontrado o no tiene contenido adjunto.', 'danger')
            return redirect(request.referrer or url_for('legajo.listar_personal'))

        # La clave está en cambiar as_attachment a False
        return send_file(
            io.BytesIO(document['data']),
            as_attachment=False, # Importante: le dice al navegador que lo muestre
            download_name=document['filename']
        )
    except Exception as e:
        current_app.logger.error(f"Error al visualizar documento {documento_id}: {e}")
        flash('Ocurrió un error al intentar mostrar el archivo.', 'danger')
        return redirect(request.referrer or url_for('legajo.listar_personal'))
    

@legajo_bp.route('/documento/<int:documento_id>/eliminar', methods=['POST'])
@login_required
@role_required('AdministradorLegajos')
def eliminar_documento(documento_id):
    """
    Gestiona la solicitud de eliminación (lógica) de un documento.
    """
    # --- INICIO DEL CÓDIGO DE SEGUIMIENTO ---
    print(f"DEBUG: Iniciando eliminación para el documento ID: {documento_id}")
    # --- FIN DEL CÓDIGO DE SEGUIMIENTO ---
    
    legajo_service = current_app.config['LEGAJO_SERVICE']
    try:
        legajo_service.delete_document_by_id(documento_id, current_user.id)
        
        flash('Documento eliminado correctamente.', 'success')

    except Exception as e:
        current_app.logger.error(f"Error al eliminar documento {documento_id}: {e}")
    
    # Redirige al usuario a la página anterior
    print("DEBUG: Redirigiendo al usuario.")
    return redirect(request.referrer or url_for('main_dashboard'))

@legajo_bp.route('/api/tipos_documento/por_seccion/<int:id_seccion>')
@login_required
def api_tipos_documento_por_seccion(id_seccion):
    """
    API endpoint para obtener los tipos de documento filtrados por sección.
    """
    try:
        legajo_service = current_app.config['LEGAJO_SERVICE']
        tipos = legajo_service.get_tipos_documento_for_seccion(id_seccion)
        return jsonify(tipos)
    except Exception as e:
        current_app.logger.error(f"Error en API de tipos de documento: {e}")
        return jsonify({"error": "No se pudieron cargar los datos"}), 500
    

@legajo_bp.route('/documento/<int:documento_id>/visualizar')
@login_required
@role_required('AdministradorLegajos', 'RRHH', 'Sistemas')
def visualizar_documento(documento_id):
        """
        Gestiona la solicitud de visualización de un archivo en el navegador.
        Sirve el archivo con el mimetype adecuado para que el navegador lo muestre en línea.
        """
        legajo_service = current_app.config['LEGAJO_SERVICE']
        try:
            document = legajo_service.get_document_for_download(documento_id)
            
            if not document or not document.get('data'):
                flash('El documento no fue encontrado o no tiene contenido adjunto.', 'danger')
                return redirect(request.referrer or url_for('main_dashboard'))

            mimetype, _ = mimetypes.guess_type(document['filename'])
            if not mimetype:
                mimetype = 'application/octet-stream'

            return send_file(
                io.BytesIO(document['data']),
                mimetype=mimetype,
                as_attachment=False, # ¡CRUCIAL! Esto le dice al navegador que lo visualice en línea
                download_name=document['filename']
            )
        except Exception as e:
            current_app.logger.error(f"Error al visualizar documento {documento_id}: {e}")
            flash('Ocurrió un error al intentar visualizar el archivo.', 'danger')
            return redirect(request.referrer or url_for('main_dashboard'))    
