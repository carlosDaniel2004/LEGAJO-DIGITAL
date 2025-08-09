# Importa las funciones de hashing y verificación de contraseñas de Werkzeug.
from werkzeug.security import generate_password_hash as werkzeug_generate_hash
from werkzeug.security import check_password_hash as werkzeug_check_hash

# Define el método de hashing scrypt con parámetros de coste recomendados.
# Esto hace que el hashing sea computacionalmente costoso y más seguro contra ataques de fuerza bruta.
SCRYPT_METHOD = "scrypt:32768:8:1"

# Define una función para generar un hash de una contraseña.
def generate_password_hash(password):
    # Llama a la función de Werkzeug especificando el método scrypt.
    return werkzeug_generate_hash(password, method=SCRYPT_METHOD)

# Define una función para verificar si una contraseña coincide con un hash existente.
def check_password_hash(pwhash, password):
    # Llama a la función de Werkzeug para realizar la comparación de forma segura.
    return werkzeug_check_hash(pwhash, password) 
