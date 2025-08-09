# Importa las librerías necesarias.
import os
import getpass
import pyodbc
from dotenv import load_dotenv

# Carga las variables de entorno desde el fichero .env.
load_dotenv()

# --- IMPORTANTE: Se importa ÚNICAMENTE la función de hashing de la app ---
# Esto es crucial para que las contraseñas generadas aquí sean compatibles con las que usa la aplicación.
from app.core.security import generate_password_hash

# --- Configuración de la Conexión Directa ---
# Lee las credenciales del administrador directamente desde las variables de entorno.
DB_DRIVER = os.environ.get('DB_DRIVER')
DB_SERVER = os.environ.get('DB_SERVER')
DB_DATABASE = os.environ.get('DB_DATABASE')
DB_USERNAME_SA = os.environ.get('DB_USERNAME_SA')
DB_PASSWORD_SA = os.environ.get('DB_PASSWORD_SA')

# Función principal de la herramienta.
def reset_user_password_direct():
    """
    Herramienta de línea de comandos para resetear la contraseña de un usuario
    conectándose directamente a la BD con un usuario administrador (ej. 'sa').
    """
    print("--- Herramienta de Reseteo Directo de Contraseña ---")
    
    try:
        # Construye la cadena de conexión.
        conn_str = f"DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USERNAME_SA};PWD={DB_PASSWORD_SA};"
        # Se conecta a la base de datos.
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("Conexión a la base de datos establecida como administrador.")

        # Solicita el nombre de usuario a modificar.
        username = input("Ingrese el nombre de usuario que desea modificar: ")
        if not username:
            print("Error: El nombre de usuario no puede estar vacío.")
            return

        # Verifica si el usuario existe antes de continuar.
        cursor.execute("SELECT COUNT(1) FROM usuarios WHERE username = ?", username)
        if cursor.fetchone()[0] == 0:
            print(f"Error: El usuario '{username}' no fue encontrado en la base de datos.")
            return

        # Solicita la nueva contraseña de forma segura.
        new_password = getpass.getpass(f"Ingrese la nueva contraseña para '{username}': ")
        if not new_password:
            print("Error: La contraseña no puede estar vacía.")
            return

        # Genera el hash de la nueva contraseña usando la misma función que la app.
        new_password_hash = generate_password_hash(new_password)
        
        # Ejecuta la sentencia UPDATE directamente.
        cursor.execute("UPDATE usuarios SET password_hash = ? WHERE username = ?", new_password_hash, username)
        conn.commit()

        print(f"\n¡Éxito! La contraseña para el usuario '{username}' ha sido actualizada directamente en la base de datos.")

    except pyodbc.Error as db_err:
        print(f"\nERROR DE BASE DE DATOS: No se pudo completar la operación.")
        print(f"Detalles: {db_err}")
    except Exception as e:
        print(f"\nOcurrió un error inesperado: {e}")
    finally:
        # Se asegura de cerrar la conexión si fue establecida.
        if 'conn' in locals() and conn:
            conn.close()

# Punto de entrada para ejecutar la herramienta.
if __name__ == '__main__':
    reset_user_password_direct()