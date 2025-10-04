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

from .application.services.solicitud_service import SolicitudService 
from .application.services.backup_service import BackupService 

from .infrastructure.persistence.sqlserver_repository import (
    SqlServerUsuarioRepository, 
    SqlServerPersonalRepository, 
    SqlServerAuditoriaRepository,
    SqlServerBackupRepository, 
    SqlServerSolicitudRepository 
)

from .presentation.routes.auth_routes import auth_bp
from .presentation.routes.legajo_routes import legajo_bp
from .presentation.routes.sistemas_routes import sistemas_bp
from .presentation.routes.rrhh_routes import rrhh_bp

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

    logging.basicConfig(level=logging.INFO)

    init_app_db(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    # Inyección de dependencias dentro del contexto de la aplicación
    with app.app_context():
        # --- 1. Inicialización de Repositorios ---
        usuario_repo = SqlServerUsuarioRepository()
        personal_repo = SqlServerPersonalRepository()
        audit_repo = SqlServerAuditoriaRepository()
        
        # Inicialización de los nuevos repositorios
        backup_repo = SqlServerBackupRepository() 
        solicitud_repo = SqlServerSolicitudRepository()
        
        app.config['USUARIO_REPOSITORY'] = usuario_repo
        app.config['PERSONAL_REPOSITORY'] = personal_repo
        app.config['AUDIT_REPOSITORY'] = audit_repo
        
        # --- 2. Inicialización de Servicios ---
        email_service = EmailService(mail)
        audit_service = AuditService(audit_repo) # Este es el servicio que necesitamos pasar
        
        # 🔑 CORRECCIÓN CRÍTICA: Se pasa audit_service al constructor del BackupService
        app.config['BACKUP_SERVICE'] = BackupService(backup_repo, app.config, audit_service)
        
        # Servicio de Solicitudes (necesario para la vista de Sistemas)
        app.config['SOLICITUDES_SERVICE'] = SolicitudService(solicitud_repo)
        
        # Servicios existentes
        app.config['USUARIO_SERVICE'] = UsuarioService(usuario_repo, email_service)
        app.config['AUDIT_SERVICE'] = audit_service
        app.config['LEGAJO_SERVICE'] = LegajoService(personal_repo, audit_service)
    
    # --- Registro de Blueprints ---
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(legajo_bp, url_prefix='/legajos')
    app.register_blueprint(sistemas_bp, url_prefix='/sistemas')

    app.register_blueprint(rrhh_bp) 

    # --- Definición de Rutas Principales ---
    @app.route('/')
    def index():
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return redirect(url_for('main_dashboard'))

    @app.route('/dashboard')
    @login_required
    def main_dashboard():
        return render_template('dashboard_main.html')
        
    return app
