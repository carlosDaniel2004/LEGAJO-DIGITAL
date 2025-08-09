class Bitacora:
    def __init__(self, id_bitacora, id_usuario, fecha_hora, modulo, accion, **kwargs):
        self.id_bitacora = id_bitacora
        self.id_usuario = id_usuario
        self.fecha_hora = fecha_hora
        self.modulo = modulo
        self.accion = accion
        self.descripcion = kwargs.get('descripcion')
        self.detalle_json = kwargs.get('detalle_json')