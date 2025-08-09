# RUTA: app/domain/models/usuario.py

from flask_login import UserMixin
from app.core.security import check_password_hash, generate_password_hash

class Usuario(UserMixin):
    """
    Representa la entidad de un usuario, incluyendo datos de sesión y perfil.
    """
    def __init__(self, id_usuario, username, id_rol, password_hash=None, activo=True, 
                 email=None, nombre_rol=None, two_factor_code=None, two_factor_expiry=None,
                 # --- INICIO DE LA MODIFICACIÓN ---
                 # Nuevos campos para el perfil del dashboard
                 nombre_completo=None, ultimo_login=None,
                 # --- FIN DE LA MODIFICACIÓN ---
                 **kwargs):
        
        self.id = id_usuario
        self.username = username
        self.id_rol = id_rol
        self.password_hash = password_hash
        self.activo = activo
        self.email = email
        self.rol = nombre_rol
        
        self.two_factor_code = two_factor_code
        self.two_factor_expiry = two_factor_expiry

        # --- INICIO DE LA MODIFICACIÓN ---
        # Asignación de los nuevos atributos
        self.nombre_completo = nombre_completo
        self.fecha_ultimo_login = ultimo_login # Renombrado para consistencia
        # --- FIN DE LA MODIFICACIÓN ---

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if self.password_hash:
            return check_password_hash(self.password_hash, password)
        return False

    def check_2fa_code(self, code):
        if self.two_factor_code:
            return check_password_hash(self.two_factor_code, code)
        return False

    @staticmethod
    def from_dict(data):
        if data:
            return Usuario(**data)
        return None
