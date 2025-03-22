document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll(".card"); // Seleccionamos todas las tarjetas
    const likeBtn = document.querySelectorAll(".like-btn"); // Seleccionamos todos los botones de like

    // Recorremos cada tarjeta y le asignamos las estrellas
    cards.forEach(card => {
        const stars = card.querySelectorAll(".star"); // Estrellas de la tarjeta
        let rating = 0;

        stars.forEach(star => {
            star.addEventListener("click", () => {
                rating = star.getAttribute("data-value");
                stars.forEach(s => s.classList.remove("active")); // Eliminamos la clase 'active' de todas las estrellas
                for (let i = 0; i < rating; i++) { // Añadimos la clase 'active' a las estrellas seleccionadas
                    stars[i].classList.add("active");
                }
            });
        });
    });

    // Lógica para el botón de like
    likeBtn.forEach(button => {
        button.addEventListener("click", () => {
            button.classList.toggle("liked");
        });
    });
});
