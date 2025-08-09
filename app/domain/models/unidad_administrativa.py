class UnidadAdministrativa:
    def __init__(self, id_unidad, nombre, **kwargs):
        self.id_unidad = id_unidad
        self.nombre = nombre
        self.ubicacion = kwargs.get('ubicacion')
        self.responsable = kwargs.get('responsable') 
