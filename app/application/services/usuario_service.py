# RUTA: app/application/services/usuario_service.py

import random
import string
from datetime import datetime, timedelta
from app.core.security import generate_password_hash
import logging # Importa la librería de logging

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
            # --- Lógica de envío de correo 2FA ---
            # Verifica si el correo existe y no es una cadena vacía después de limpiar espacios
            if user.email and user.email.strip(): 
                try:
                    self._email_service.send_2fa_code(user.email, user.username, code)
                    logger.info(f"Correo 2FA enviado a {user.email} para usuario {user.username}.")
                except ConnectionError as e:
                    # Captura el error específico que podría lanzar EmailService
                    logger.error(f"Error al enviar email de 2FA a {user.email}: {e}")
                    # Vuelve a lanzar el error para que la ruta lo maneje
                    raise
                except Exception as e:
                    # Captura cualquier otro error inesperado durante el envío
                    logger.error(f"Error inesperado al enviar email de 2FA a {user.email}: {e}")
                    raise ConnectionError("No se pudo enviar el correo de verificación debido a un error inesperado.")
            else:
                # Si el correo no es válido, registra una advertencia y no intenta enviar el email
                logger.warning(f"El usuario '{username}' no tiene un correo electrónico válido registrado ('{user.email}'). No se enviará el código 2FA por email.")
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

