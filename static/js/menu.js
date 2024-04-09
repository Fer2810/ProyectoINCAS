// JavaScript to toggle the sidebar menu
var menuToggle = document.getElementById('menu-toggle');
var sidebar = document.getElementById('sidebar');

menuToggle.addEventListener('click', function() {
    sidebar.classList.toggle('open');
});

// JavaScript para el carrusel
var slides = document.querySelectorAll('.slide');
var currentSlide = 0;

function showSlide(n) {
    slides[currentSlide].classList.remove('active');
    currentSlide = (n + slides.length) % slides.length;
    slides[currentSlide].classList.add('active');
}

function nextSlide() {
    showSlide(currentSlide + 1);
}

setInterval(nextSlide, 3000); // Cambiar cada 3 segundos