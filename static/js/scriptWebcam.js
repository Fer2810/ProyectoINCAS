// JavaScript to toggle the sidebar menu
var menuToggle = document.getElementById('menu-toggle');
var sidebar = document.getElementById('sidebar');

menuToggle.addEventListener('click', function() {
    sidebar.classList.toggle('open');
});