# RUTA: app/application/services/usuario_service.py

import random
import string
from datetime import datetime, timedelta
from app.core.security import generate_password_hash
import logging 

# Configura un logger para este módulo
logger = logging.getLogger(__name__)

class UsuarioService:
    def __init__(self, usuario_repository, email_service):
        self._usuario_repo = usuario_repository
        self._email_service = email_service

    def attempt_login(self, username, password):
        """Verifica las credenciales. Si son válidas, genera y muestra el código 2FA para desarrollo."""
        user = self._usuario_repo.find_by_username_with_email(username)

        if user and user.activo and user.check_password(password):
            code = ''.join(random.choices(string.digits, k=6))
            hashed_code = generate_password_hash(code)
            expiry_date = datetime.utcnow() + timedelta(minutes=10)

            self._usuario_repo.set_2fa_code(user.id, hashed_code, expiry_date)

            print("---------------------------------------------------------")
            print(f"--- CÓDIGO 2FA (PARA DESARROLLO): {code} ---")
            print("---------------------------------------------------------")
            """
            # --- Lógica de envío de correo 2FA (comentada) ---
            # ... (código para enviar el email) ...
            """
            return user.id
        
        return None

    def verify_2fa_code(self, user_id, code):
        """Verifica el código 2FA proporcionado por el usuario."""
        user = self._usuario_repo.find_by_id(user_id)
        
        if not user or not user.two_factor_code or user.two_factor_expiry < datetime.utcnow():
            return None

        if user.check_2fa_code(code):
            self._usuario_repo.clear_2fa_code(user.id)
            return user
        
        return None

    def update_last_login(self, user_id):
        """Orquesta la actualización de la fecha del último login para un usuario."""
        self._usuario_repo.update_last_login(user_id)

    # ====================================================================
    # >>> MÉTODO AGREGADO: get_all_users_with_roles <<<
    #    Este método corrige el 'AttributeError'.
    # ====================================================================
    def get_all_users_with_roles(self):
        """
        Obtiene todos los usuarios y los mapea con su información de rol,
        llamando a la capa de repositorio.
        """
        try:
            # Debe asegurarse de que su UsuarioRepository (self._usuario_repo)
            # tenga implementado el método 'find_all_users_with_roles()'.
            usuarios_con_roles = self._usuario_repo.find_all_users_with_roles()
            logger.info("Usuarios con roles obtenidos correctamente para la gestión.")
            return usuarios_con_roles
        except Exception as e:
            logger.error(f"Error al obtener todos los usuarios con roles desde el repositorio: {e}")
            # Devolvemos una lista vacía para evitar un crash si la BD falla
            return []