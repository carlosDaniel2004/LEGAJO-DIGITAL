# RUTA: app/decorators.py

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def role_required(*roles):
    """
    Decorador para restringir el acceso a rutas según una lista de nombres de roles permitidos.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Si el usuario no está autenticado, siempre se le envía a la página de login.
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            # --- INICIO DE LA CORRECCIÓN ---
            # Se verifica si el atributo 'rol' existe y si su valor (el nombre del rol, ej: "Sistemas")
            # está en la tupla de roles permitidos que se pasa al decorador.
            if not hasattr(current_user, 'rol') or current_user.rol not in roles:
            # --- FIN DE LA CORRECCIÓN ---
                # Si el rol no es el correcto, muestra un mensaje de error.
                flash('No tiene los permisos necesarios para acceder a esta página.', 'danger')
                # Se redirige a la ruta raíz 'index', que sabe a qué dashboard enviar al usuario.
                return redirect(url_for('index'))
                
            # Si el rol es correcto, se permite el acceso a la ruta.
            return f(*args, **kwargs)
        return decorated_function
    return decorator