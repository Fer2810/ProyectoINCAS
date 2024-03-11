document.addEventListener('DOMContentLoaded', function(){
    // Llamar al botón que cierra la cámara
    var cerrarCamaraBtn = document.getElementById('cerrar-camara');

    // Clic del botón
    cerrarCamaraBtn.addEventListener('click', function(){
        // Realizar solicitud al servidor para cerrar la cámara
        fetch('/cerrar_camara')
        .then(Response=>Response.json())
        .then(data=>{
            // Manejar la respuesta en el servidor
            console.log(data);
            // Indicar un cambio de vista después de cerrar la cámara
            set_cambio_vista();
        })
        .catch(error=> {
            console.error('Error al cerrar la cámara', error);
        });
    });
});
