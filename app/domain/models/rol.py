# Define la clase Rol.
# Representa un rol de usuario dentro del sistema (ej. Administrador, RRHH).
class Rol:
    # El constructor define los atributos del objeto.
    def __init__(self, id_rol, nombre_rol, **kwargs):
        self.id_rol = id_rol
        self.nombre_rol = nombre_rol 
