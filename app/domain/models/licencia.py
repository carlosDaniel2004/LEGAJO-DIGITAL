class Licencia:
    def __init__(self, id_licencia, id_personal, id_tipo_licencia, fecha_inicio, fecha_fin, **kwargs):
        self.id_licencia = id_licencia
        self.id_personal = id_personal
        self.id_tipo_licencia = id_tipo_licencia
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.resolucion = kwargs.get('resolucion') 
