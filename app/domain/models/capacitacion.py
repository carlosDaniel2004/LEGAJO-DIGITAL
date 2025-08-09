class Capacitacion:
    def __init__(self, id_capacitacion, id_personal, nombre_evento, fecha_inicio, **kwargs):
        self.id_capacitacion = id_capacitacion
        self.id_personal = id_personal
        self.nombre_evento = nombre_evento
        self.fecha_inicio = fecha_inicio
        self.organizador = kwargs.get('organizador')
        self.fecha_fin = kwargs.get('fecha_fin')
        self.duracion_horas = kwargs.get('duracion_horas')
        self.ruta_certificado = kwargs.get('ruta_certificado')