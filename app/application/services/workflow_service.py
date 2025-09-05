# app/application/services/workflow_service.py

class WorkflowService:
    def __init__(self, repository):
        self.repository = repository

    def get_pending_modification_requests(self):
        """
        Obtiene la lista de solicitudes de modificación que están pendientes.
        """
        try:
            requests = self.repository.get_pending_requests()
            return requests, None
        except Exception as e:
            return [], f"Error al obtener las solicitudes pendientes: {e}"

    def process_request(self, request_id, action, reviewer_id):
        """
        Procesa una solicitud, ya sea aprobándola o rechazándola.
        """
        # Mapea la acción del botón a un estado válido en la base de datos
        valid_statuses = {"aprobar": "aprobada", "rechazar": "rechazada"}
        new_status = valid_statuses.get(action)

        if not new_status:
            return "Acción no válida.", "danger"

        try:
            # Por ahora, no se añaden observaciones, pero el SP lo permite
            observations = f"Solicitud procesada por el administrador."
            self.repository.process_modification_request(request_id, new_status, reviewer_id, observations)
            return f"La solicitud ha sido {new_status}.", "success"
        except Exception as e:
            return f"Error al procesar la solicitud: {e}", "danger"        