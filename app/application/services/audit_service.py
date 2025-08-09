# Importa la librería para manejar formato JSON.
import json

# Define el servicio para la lógica de negocio de auditoría.
class AuditService:
    # El constructor inyecta la dependencia del repositorio de auditoría.
    def __init__(self, auditoria_repository):
        self._audit_repo = auditoria_repository

    # Orquesta el registro de un evento.
    def log(self, id_usuario, modulo, accion, descripcion, detalle_dict=None):
        detalle_json = None
        # Convierte el diccionario de detalles a un string JSON si existe.
        if detalle_dict:
            detalle_json = json.dumps(detalle_dict, default=str)
        
        # Llama al método del repositorio para guardar el evento en la base de datos.
        self._audit_repo.log_event(id_usuario, modulo, accion, descripcion, detalle_json)

    # Orquesta la obtención de los registros de auditoría.
    def get_logs(self, page, per_page):
        return self._audit_repo.get_all_logs_paginated(page, per_page) 
