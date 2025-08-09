class HistorialLaboral:
    def __init__(self, id_historial, id_personal, id_cargo, id_unidad, fecha_inicio, **kwargs):
        self.id_historial = id_historial
        self.id_personal = id_personal
        self.id_cargo = id_cargo
        self.id_unidad = id_unidad
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = kwargs.get('fecha_fin')
        self.motivo_salida = kwargs.get('motivo_salida') 
