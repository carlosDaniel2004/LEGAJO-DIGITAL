from abc import ABC, abstractmethod

# Define la interfaz para el repositorio de Auditoría.
class IAuditoriaRepository(ABC):
    # Contrato para un método que registrará un nuevo evento en la bitácora.
    @abstractmethod
    def log_event(self, id_usuario, modulo, accion, descripcion, detalle_json=None):
        pass

    # Contrato para un método que obtendrá una lista paginada de todos los registros de la bitácora.
    @abstractmethod
    def get_all_logs_paginated(self, page, per_page):
        pass 
