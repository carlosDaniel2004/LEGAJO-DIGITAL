class Contrato:
    def __init__(self, id_contrato, id_personal, id_tipo_contrato, fecha_inicio, sueldo, **kwargs):
        self.id_contrato = id_contrato
        self.id_personal = id_personal
        self.id_tipo_contrato = id_tipo_contrato
        self.fecha_inicio = fecha_inicio
        self.sueldo = sueldo
        self.fecha_fin = kwargs.get('fecha_fin')
        self.modalidad = kwargs.get('modalidad')
        self.resolucion = kwargs.get('resolucion') 
