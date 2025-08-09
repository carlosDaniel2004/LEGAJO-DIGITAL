# Importa las herramientas para crear clases abstractas (interfaces).
from abc import ABC, abstractmethod

# Define la interfaz para el Repositorio de Personal.
# Cualquier clase que implemente esta interfaz debe definir estos métodos.
class IPersonalRepository(ABC):
    @abstractmethod
    def find_by_id(self, personal_id):
        pass

    @abstractmethod
    def get_all_paginated(self, page, per_page, filters=None):
        pass

    @abstractmethod
    def create(self, personal_data):
        pass

    @abstractmethod
    def update(self, personal_id, personal_data):
        pass

    @abstractmethod
    def add_document(self, document_data, file_bytes):
        pass

    @abstractmethod
    def delete_by_id(self, personal_id):
        pass

    @abstractmethod
    def find_documents_by_personal_id(self, personal_id):
        pass

    @abstractmethod
    def find_document_by_id(self, document_id):
        """Define el contrato para buscar un único documento por su ID."""
        pass

    @abstractmethod
    def delete_document_by_id(self, document_id):
        """Define el contrato para la eliminación lógica de un documento."""
        pass