window.onload = function() {
    // Obtenemos el contenedor con los productos desde el HTML
    const productosElement = document.getElementById('platos');
    
    if (productosElement) {  // Verificar si el contenedor existe
        const productosJSON = productosElement.getAttribute('data-platos');
        console.log(productosElement);
        console.log(productosJSON);

        try {
            // Parseamos el JSON desde el atributo 'data-productos'
            const productos = JSON.parse(productosJSON);
            mostrarPlatos(productos);
        } catch (error) {
            console.error("Error al parsear el JSON de productos:", error);
        }
    } else {
        console.error("El elemento 'productos' no se encuentra en el DOM");
    }
};


// Función para mostrar los platos en el HTML
function mostrarPlatos(platos) {
    const menuContainer = document.querySelector('.menu-container');
     // Obtenemos el codigo de premio desde el HTML
     const codigo_dcto = parseInt(document.getElementById('codigo_premio').dataset.codigo, 10);
     console.log(codigo_dcto);

    // Generar la lista de platos
    platos.forEach(plato => {
        let precioConDescuento;
        // Definir el descuento a usar
        const descuento = (plato.constante==1) ? plato.dcto : (codigo_dcto == 0 ? plato.dcto : codigo_dcto);
        // Calcular el precio con el descuento elegido
        precioConDescuento = (plato.precioVenta - (plato.precioVenta * descuento / 100)).toFixed(2);
        //const imagenURL = "{{ url_for('static', filename='') }}" + plato.imagen;
        const imagenURL = "/static/" + plato.imagen;
        const platoDiv = document.createElement("div");
        platoDiv.className = 'plato';

        platoDiv.innerHTML = `
        <div class="plato" id="plato-${plato.id_plato}">
            <img src="${imagenURL}" alt="${plato.nombre}" loading="lazy">
            <div class="plato-info">
                <h3 class="nombre-plato">${plato.nombre}</h3>
                <p class="descripcion-plato">${plato.descPlato}</p>
            </div>
            <div class="precios">
                <p class="precio-original">S/${plato.precioVenta}</p>
                <p class="precio-descuento">S/${precioConDescuento}</p>
                <button class="agregar" onclick="agregarAlCarrito(${plato.id_plato}, '${plato.nombre}', ${precioConDescuento})">Agregar</button>
            </div>
        </div>
        `;
        menuContainer.appendChild(platoDiv);
        /*menuContainer.innerHTML += platoHTML;*/
    });
}