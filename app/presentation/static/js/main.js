// Espera a que todo el contenido del DOM esté cargado antes de ejecutar el script.
window.addEventListener('DOMContentLoaded', event => {
    // Busca el botón que controla el menú lateral.
    const sidebarToggle = document.body.querySelector('#menu-toggle');
    if (sidebarToggle) {
        // Añade un 'event listener' para el evento 'click'.
        sidebarToggle.addEventListener('click', event => {
            // Previene el comportamiento por defecto del botón.
            event.preventDefault();
            // Añade o quita la clase 'toggled' al contenedor principal para mostrar/ocultar el menú.
            document.getElementById('wrapper').classList.toggle('toggled');
        });
    }
}); 
