var menuToggle = document.getElementById('menu-toggle');
var sidebar = document.getElementById('sidebar');

menuToggle.addEventListener('click', function() {
    sidebar.classList.toggle('open');
});

var administradores = [];

function mostrarAdmins() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("tablaAdmins").getElementsByTagName('tbody')[0].innerHTML = this.responseText;
        }
    };
    xhttp.open("GET", "mostrar_administradores.php", true);
    xhttp.send();
}

function modificarAdmin(idAdmin) {
    var nuevoNombre = prompt("Ingrese el nuevo nombre del administrador:");
    // Similar para otros campos
    if (nuevoNombre !== null) {
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                mostrarAdmins(); // Actualizar la tabla después de la modificación
            }
        };
        xhttp.open("POST", "modificar_administrador.php", true);
        xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhttp.send("idAdmin=" + idAdmin + "&nuevoNombre=" + nuevoNombre);
    }
}

function eliminarAdmin() {
    var tabla = document.getElementById("tablaAdmins").getElementsByTagName('tbody')[0];
    var rowCount = tabla.rows.length;

    if (rowCount > 0) {
        tabla.deleteRow(rowCount - 1);
    } else {
        alert("No hay administradores para eliminar.");
    }
}