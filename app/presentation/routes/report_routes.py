# RUTA: app/presentation/routes/report_routes.py

from flask import Blueprint, redirect, render_template, current_app, send_file, flash, url_for
from flask_login import login_required
from app.decorators import role_required

report_bp = Blueprint('reports', __name__)

@report_bp.route('/general/personal')
@login_required
@role_required('AdministradorLegajos', 'RRHH', 'Sistemas')
def reporte_general_personal():
    return render_template('reports/generar_reporte.html')

@report_bp.route('/general/personal/exportar')
@login_required
@role_required('AdministradorLegajos', 'RRHH', 'Sistemas')
def exportar_reporte_general():
    try:
        legajo_service = current_app.config['LEGAJO_SERVICE']
        excel_stream = legajo_service.generate_general_report_excel()
        
        # Envía el fichero Excel generado al navegador del usuario para su descarga.
        return send_file(
            excel_stream,
            as_attachment=True,
            download_name='Reporte_General_Personal.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        current_app.logger.error(f"Error al generar reporte general: {e}")
        flash("Ocurrió un error al generar el reporte.", "danger")
        return redirect(url_for('reports.reporte_general_personal'))