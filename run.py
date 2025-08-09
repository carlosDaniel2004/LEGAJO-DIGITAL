# Importa la función que crea y configura la aplicación Flask.
from app import create_app

# Crea una instancia de la aplicación llamando a la factoría.
app = create_app()

# Punto de entrada para ejecutar la aplicación.
# Se activa solo cuando el script es ejecutado directamente.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)


#if __name__ == '__main__':
    # Inicia el servidor de desarrollo de Flask.
    # El modo debug se debe desactivar en producción.
    #app.run(debug=True) 
