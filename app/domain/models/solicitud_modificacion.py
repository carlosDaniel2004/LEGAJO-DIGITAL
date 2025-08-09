class SolicitudModificacion:
    def __init__(self, id_solicitud, id_personal, id_usuario_solicitante, campo_modificado, **kwargs):
        self.id_solicitud = id_solicitud
        self.id_personal = id_personal
        self.id_usuario_solicitante = id_usuario_solicitante
        self.campo_modificado = campo_modificado
        self.fecha_solicitud = kwargs.get('fecha_solicitud')
        self.valor_anterior = kwargs.get('valor_anterior')
        self.valor_nuevo = kwargs.get('valor_nuevo')
        self.estado = kwargs.get('estado', 'pendiente')
        self.observaciones = kwargs.get('observaciones')
        self.id_usuario_revisor = kwargs.get('id_usuario_revisor')
        self.fecha_revision = kwargs.get('fecha_revision') 
