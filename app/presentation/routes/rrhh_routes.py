# app/presentation/routes/rrhh_routes.py

from flask import Blueprint, render_template
from flask_login import current_user
# --- INICIO DE LA CORRECCIÓN ---
from flask_login import login_required
from app.decorators import role_required
# --- FIN DE LA CORRECCIÓN ---

# Creamos el Blueprint para el rol de RRHH
# Todas las rutas definidas aquí comenzarán con /rrhh
rrhh_bp = Blueprint('rrhh', __name__, url_prefix='/rrhh')

@rrhh_bp.route('/dashboard')
@login_required
@role_required('RRHH')
def dashboard():
    """
    Dashboard principal para el rol de Recursos Humanos.
    """
    return render_template('rrhh/dashboard.html', user=current_user)

# Aquí se agregarán más rutas para el rol de RRHH en el futuro.