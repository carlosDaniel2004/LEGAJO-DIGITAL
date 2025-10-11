# RUTA: app/application/services/solicitud_service.py

class SolicitudService:
    """
    Servicio de aplicación para gestionar las solicitudes de modificación.
    Se conecta al repositorio de solicitudes.
    """
    def __init__(self, solicitud_repository):
        # El repositorio ya se crea y se pasa desde app/__init__.py
        self.solicitud_repo = solicitud_repository

    def get_all_pending(self):
        """Obtiene todas las solicitudes que están en estado pendiente."""
        # Se asume que el repositorio devuelve una lista de diccionarios o modelos.
        # Aquí es donde el servicio llamaría a solicitud_repo.get_pending_requests()
        # Si no hay implementación, devuelve una lista vacía para evitar errores.
        try:
            return self.solicitud_repo.get_pending_requests()
        except Exception:
            # En un entorno real, manejaríamos el logging. Aquí devolvemos vacío para no romper la app.
            return []

    def process_request(self, request_id, action):
        """Procesa la aprobación o rechazo de una solicitud."""
        # Llama a la lógica de persistencia.
        return self.solicitud_repo.process_request(request_id, action)