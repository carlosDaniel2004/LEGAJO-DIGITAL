from flask import Blueprint, render_template, request, current_app
from flask_login import login_required, current_user
from app.decorators import role_required

# Blueprint para las funcionalidades exclusivas del rol de Sistemas.
sistemas_bp = Blueprint('sistemas', __name__)

@sistemas_bp.route('/dashboard')
@login_required
@role_required('Sistemas')
def dashboard():
    return render_template('sistemas/dashboard.html', username=current_user.username)

@sistemas_bp.route('/auditoria')
@login_required
@role_required('Sistemas')
def auditoria():
    page = request.args.get('page', 1, type=int)
    audit_service = current_app.config['AUDIT_SERVICE']
    pagination = audit_service.get_logs(page, 20)
    audit_service.log(current_user.id, 'Auditoria', 'CONSULTA', f'El usuario consultó la página {page} de la bitácora.')
    return render_template('sistemas/auditoria.html', pagination=pagination)

@sistemas_bp.route('/reportes')
@login_required
@role_required('Sistemas')
def reportes():
    # Esta es la página principal de reportes para el admin de sistemas.
    return render_template('sistemas/reportes.html')