// RUTA: app/presentation/static/js/main.js

// Espera a que todo el contenido del DOM esté cargado.
window.addEventListener('DOMContentLoaded', event => {
    // Lógica para el botón de mostrar/ocultar la barra lateral
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.getElementById('wrapper').classList.toggle('toggled');
        });
    }

    // Puedes añadir más lógica de JavaScript global aquí en el futuro.
});
