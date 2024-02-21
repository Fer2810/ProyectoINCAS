document.getElementById("toggleButton").addEventListener("click", function() {
    var docenteForm = document.getElementById("docente-form");
    var adminForm = document.getElementById("admin-form");
    var button = document.getElementById("toggleButton");

    if (docenteForm.style.display === "block") {
        docenteForm.style.display = "none";
        adminForm.style.display = "block";
        button.textContent = "Cambiar a Docente";
    } else {
        docenteForm.style.display = "block";
        adminForm.style.display = "none";
        button.textContent = "Cambiar a Administrador";
    }
});
