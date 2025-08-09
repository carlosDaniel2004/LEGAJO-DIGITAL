# Define la clase Personal.
# Representa los datos de un empleado.
class Personal:
    def __init__(self, id_personal, dni, nombres, apellidos, **kwargs):
        self.id_personal = id_personal
        self.dni = dni
        self.nombres = nombres
        self.apellidos = apellidos
        # kwargs permite manejar campos opcionales de la tabla.
        self.sexo = kwargs.get('sexo')
        self.fecha_nacimiento = kwargs.get('fecha_nacimiento')
        self.direccion = kwargs.get('direccion')
        self.telefono = kwargs.get('telefono')
        self.email = kwargs.get('email')
        self.estado_civil = kwargs.get('estado_civil')
        self.nacionalidad = kwargs.get('nacionalidad')
        self.id_unidad = kwargs.get('id_unidad')
        self.activo = kwargs.get('activo', True)
        self.fecha_ingreso = kwargs.get('fecha_ingreso')
        self.fecha_registro = kwargs.get('fecha_registro')

    @staticmethod
    def from_dict(data):
        return Personal(**data)