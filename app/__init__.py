# RUTA: app/__init__.py

import logging
from flask import Flask, redirect, url_for, current_app, render_template
from flask_login import LoginManager, current_user, login_required
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail

from .config import Config
from .database.connector import init_app_db
from .domain.models.usuario import Usuario
from .application.services.email_service import EmailService
from .application.services.usuario_service import UsuarioService
from .application.services.legajo_service import LegajoService
from .application.services.audit_service import AuditService
from .infrastructure.persistence.sqlserver_repository import (
    SqlServerUsuarioRepository, SqlServerPersonalRepository, SqlServerAuditoriaRepository
)
from .presentation.routes.auth_routes import auth_bp
from .presentation.routes.legajo_routes import legajo_bp
from .presentation.routes.sistemas_routes import sistemas_bp

# Inicialización de extensiones de Flask
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = "Por favor, inicie sesión para acceder a esta página."
login_manager.login_message_category = "info"
csrf = CSRFProtect()
mail = Mail()

@login_manager.user_loader
def load_user(user_id):
    """Carga el usuario para la sesión de Flask-Login."""
    repo = current_app.config.get('USUARIO_REPOSITORY')
    if repo:
        return repo.find_by_id(int(user_id))
    return None

def create_app():
    """
    Factoría de la aplicación Flask.
    Configura la app, inicializa extensiones, registra blueprints y define rutas.
    """
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder='presentation/templates',
        static_folder='presentation/static'
    )
    app.config.from_object(Config)

    # Configuración de logging
    logging.basicConfig(level=logging.INFO)

    # Inicialización de extensiones con la app
    init_app_db(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    # Inyección de dependencias dentro del contexto de la aplicación
    with app.app_context():
        usuario_repo = SqlServerUsuarioRepository()
        personal_repo = SqlServerPersonalRepository()
        audit_repo = SqlServerAuditoriaRepository()
        
        app.config['USUARIO_REPOSITORY'] = usuario_repo
        app.config['PERSONAL_REPOSITORY'] = personal_repo
        app.config['AUDIT_REPOSITORY'] = audit_repo
        
        email_service = EmailService(mail)
        audit_service = AuditService(audit_repo)
        
        app.config['USUARIO_SERVICE'] = UsuarioService(usuario_repo, email_service)
        app.config['AUDIT_SERVICE'] = audit_service
        app.config['LEGAJO_SERVICE'] = LegajoService(personal_repo, audit_service)
    
    # --- Registro de Blueprints ---
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(legajo_bp, url_prefix='/legajos')
    app.register_blueprint(sistemas_bp, url_prefix='/sistemas')

    # --- Definición de Rutas Principales ---
    # Todas las rutas deben definirse dentro de la función create_app
    
    @app.route('/')
    def index():
        """
        Ruta raíz. Redirige al login si no está autenticado,
        o al dashboard principal si lo está.
        """
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return redirect(url_for('main_dashboard'))

    @app.route('/dashboard')
    @login_required
    def main_dashboard():
        """
        Muestra la página principal del dashboard con las tarjetas de opciones,
        según el diseño del prototipo.
        """
        return render_template('dashboard_main.html')
        
    return app
