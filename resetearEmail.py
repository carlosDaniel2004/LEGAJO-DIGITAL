# Importa las librerías necesarias.
import os
import pyodbc
from dotenv import load_dotenv

# Carga las variables de entorno desde el fichero .env.
load_dotenv()

# --- Configuración de la Conexión Directa ---
# Lee las credenciales del administrador directamente desde las variables de entorno.
DB_DRIVER = os.environ.get('DB_DRIVER')
DB_SERVER = os.environ.get('DB_SERVER')
DB_DATABASE = os.environ.get('DB_DATABASE')
DB_USERNAME_SA = os.environ.get('DB_USERNAME_SA')
DB_PASSWORD_SA = os.environ.get('DB_PASSWORD_SA')

# Función principal de la herramienta.
def update_user_email_direct():
    """
    Herramienta de línea de comandos para actualizar el correo electrónico de un usuario
    conectándose directamente a la BD con un usuario administrador (ej. 'sa').
    """
    print("--- Herramienta de Actualización Directa de Correo Electrónico ---")
    
    conn = None # Inicializa conn a None
    try:
        # Construye la cadena de conexión.
        conn_str = (
            f"DRIVER={DB_DRIVER};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_DATABASE};"
            f"UID={DB_USERNAME_SA};"
            f"PWD={DB_PASSWORD_SA};"
        )
        # Se conecta a la base de datos.
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("Conexión a la base de datos establecida como administrador.")

        # Solicita el nombre de usuario a modificar.
        username = input("Ingrese el nombre de usuario cuyo correo desea modificar: ")
        if not username:
            print("Error: El nombre de usuario no puede estar vacío.")
            return

        # Verifica si el usuario existe antes de continuar.
        cursor.execute("SELECT COUNT(1) FROM usuarios WHERE username = ?", username)
        if cursor.fetchone()[0] == 0:
            print(f"Error: El usuario '{username}' no fue encontrado en la base de datos.")
            return

        # Solicita el nuevo correo electrónico.
        new_email = input(f"Ingrese el nuevo correo electrónico para '{username}': ")
        if not new_email:
            print("Error: El correo electrónico no puede estar vacío.")
            return

        # Ejecuta la sentencia UPDATE directamente.
        # Asegúrate de que tu tabla 'usuarios' tiene una columna llamada 'email'.
        cursor.execute("UPDATE usuarios SET email = ? WHERE username = ?", new_email, username)
        conn.commit()

        print(f"\n¡Éxito! El correo electrónico para el usuario '{username}' ha sido actualizado a '{new_email}' directamente en la base de datos.")

    except pyodbc.Error as db_err:
        print(f"\nERROR DE BASE DE DATOS: No se pudo completar la operación.")
        print(f"Detalles: {db_err}")
    except Exception as e:
        print(f"\nOcurrió un error inesperado: {e}")
    finally:
        # Se asegura de cerrar la conexión si fue establecida.
        if conn:
            conn.close()

# Punto de entrada para ejecutar la herramienta.
if __name__ == '__main__':
    update_user_email_direct()
