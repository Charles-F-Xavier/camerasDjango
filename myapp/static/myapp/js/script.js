const hamBurger = document.querySelector(".toggle-btn");
const sidebarIcon = document.querySelector("#sidebar-icon");
const sidebarLogo = document.querySelector("#sidebar-logo");

hamBurger.addEventListener("click", function (event) {
    document.querySelector("#sidebar").classList.toggle("expand");

    // Detectar si se hizo clic en el ícono o en la imagen
    if (event.target === sidebarIcon) {
        sidebarIcon.classList.add("animate__fadeInLeft"); // Cambiado a fadeInRight
        //sidebarLogo.classList.remove("animate__fadeInLeft"); // Cambiado a fadeInLeft
    } else if (event.target === sidebarLogo) {
        sidebarLogo.classList.add("animate__fadeInRight"); // Cambiado a fadeInLeft
        //sidebarIcon.classList.remove("animate__fadeInRight"); // Cambiado a fadeInRight
    }
});


document.getElementById('camera-dropdown').addEventListener('click', function (event) {
    if (event.target.tagName.toLowerCase() === 'a') {
        const cameraCount = event.target.textContent;

        // Envía la solicitud al servidor (usando AJAX o fetch)
        fetch(`/?count=${cameraCount}`, {method: 'GET'}) // Usa POST
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error al actualizar las cámaras');
                }
            })
            .catch(error => {
                console.error(error);
                // Maneja el error, por ejemplo, mostrando un mensaje al usuario
            });
    }
});