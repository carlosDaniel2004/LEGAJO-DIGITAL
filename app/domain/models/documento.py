class Documento:
    def __init__(self, id_documento, id_personal, id_tipo, id_seccion, nombre_archivo, **kwargs):
        self.id_documento = id_documento
        self.id_personal = id_personal
        self.id_tipo = id_tipo
        self.id_seccion = id_seccion
        self.nombre_archivo = nombre_archivo
        self.fecha_subida = kwargs.get('fecha_subida')
        self.fecha_emision = kwargs.get('fecha_emision')
        self.fecha_vencimiento = kwargs.get('fecha_vencimiento')
        self.descripcion = kwargs.get('descripcion')
        self.archivo_guid = kwargs.get('archivo_guid')
        self.hash_archivo = kwargs.get('hash_archivo')