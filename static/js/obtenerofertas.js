window.onload = function() {
    // Obtenemos el contenedor con los productos desde el HTML
    const productosElement = document.getElementById('productos');
    
    if (productosElement) {  // Verificar si el contenedor existe
        const productosJSON = productosElement.getAttribute('data-productos');
        console.log(productosElement);
        console.log(productosJSON);

        try {
            // Parseamos el JSON desde el atributo 'data-productos'
            const productos = JSON.parse(productosJSON);
            obtenerOferta(productos);
        } catch (error) {
            console.error("Error al parsear el JSON de productos:", error);
        }
    } else {
        console.error("El elemento 'productos' no se encuentra en el DOM");
    }
};


function obtenerOferta(productos) {
    const carousel = document.getElementById('carousel');
    productos.forEach((producto, index) => {
        const precioConDescuento = (producto.precioVenta - (producto.precioVenta * producto.dcto / 100)).toFixed(2);
        const imagenURL = "/static/" + producto.imagen;

        const itemHTML = `
                <div class="carousel-item">
                    <img src="${imagenURL}" alt="${producto.nombre}" loading="lazy">
                    <div class="text-overlay">
                        <h3>${producto.nombre}</h3>
                        <p class="price">S/${producto.precioVenta}</p>
                        <p class="discount-price">S/${precioConDescuento}</p>
                        <p class="carousel-description">${producto.descPlato}</p>
                    </div>
                </div>
            `;
        carousel.innerHTML += itemHTML;
    });

    let currentIndex = 0;

    function updateCarousel() {
        const offset = -currentIndex * 100;
        carousel.style.transform = `translateX(${offset}%)`;
    }

    setInterval(() => {
        currentIndex = (currentIndex + 1) % productos.length;
        updateCarousel();
    }, 4000);
}



