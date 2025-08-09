class Estudio:
    def __init__(self, id_estudio, id_personal, nivel_educativo, institucion, **kwargs):
        self.id_estudio = id_estudio
        self.id_personal = id_personal
        self.nivel_educativo = nivel_educativo
        self.institucion = institucion
        self.carrera = kwargs.get('carrera')
        self.fecha_inicio = kwargs.get('fecha_inicio')
        self.fecha_fin = kwargs.get('fecha_fin')
        self.titulo_obtenido = kwargs.get('titulo_obtenido') 
