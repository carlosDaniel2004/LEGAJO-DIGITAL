# Importa la librería 'os' para interactuar con el sistema operativo.
import os
# Importa la función para cargar variables de entorno desde un archivo .env.
from dotenv import load_dotenv

# Carga las variables definidas en el archivo .env en el entorno actual.
load_dotenv()

# Define una clase 'Config' para centralizar todas las configuraciones de la aplicación.
class Config:
    # Carga la clave secreta desde las variables de entorno, esencial para la seguridad de Flask.
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Carga las credenciales y detalles de conexión para la base de datos.
    DB_DRIVER = os.environ.get('DB_DRIVER')
    DB_SERVER = os.environ.get('DB_SERVER')
    DB_DATABASE = os.environ.get('DB_DATABASE')
    DB_USERNAME_WRITE = os.environ.get('DB_USERNAME_WRITE')
    DB_PASSWORD_WRITE = os.environ.get('DB_PASSWORD_WRITE')
    DB_USERNAME_READ = os.environ.get('DB_USERNAME_READ')
    DB_PASSWORD_READ = os.environ.get('DB_PASSWORD_READ')

    # Carga la configuración para el servicio de envío de correos electrónicos.
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') 

        # --- CONFIGURACIÓN PARA LA SUBIDA DE ARCHIVOS ---
    # Define las extensiones de archivo permitidas (en minúsculas)
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx'}
    
    # Define el tamaño máximo del archivo en bytes (ej. 5MB)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
