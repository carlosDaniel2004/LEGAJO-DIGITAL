# Importa ABC (Abstract Base Class) y abstractmethod para definir una interfaz.
from abc import ABC, abstractmethod

# Define la interfaz 'IUsuarioRepository'.
# Cualquier clase que implemente esta interfaz debe proporcionar una implementación para todos sus métodos.
class IUsuarioRepository(ABC):
    # Método abstracto para buscar un usuario por su ID.
    @abstractmethod
    def find_by_id(self, user_id):
        pass

    # Método abstracto para buscar un usuario por su nombre de usuario e incluir su email.
    @abstractmethod
    def find_by_username_with_email(self, username):
        pass

    # Método abstracto para guardar el código 2FA y su fecha de expiración para un usuario.
    @abstractmethod
    def set_2fa_code(self, user_id, hashed_code, expiry_date):
        pass

    # Método abstracto para limpiar los datos del código 2FA de un usuario.
    @abstractmethod
    def clear_2fa_code(self, user_id):
        pass 

    # --- AÑADE este método DENTRO de la clase IUsuarioRepository ---
    @abstractmethod
    def update_password_hash(self, username, new_hash):
        pass

    @abstractmethod
    def update_last_login(self, user_id):
        """Define el contrato para actualizar la fecha del último login."""
        pass
