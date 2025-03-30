
// Precios base por tipo de campo
const precios = {
    "General": {
        "Adulto": null,
        "Niño": null,
        "Tercera Edad": null
    },
    "VIP": {
        "Adulto": null,
        "Niño": null,
        "Tercera Edad": null
    },
    "Platinum": {
        "Adulto": null,
        "Niño": null,
        "Tercera Edad": null
    }
};

function actualizarPrecio() {
    const nombreCampo = document.getElementById("nombreCampo").value;
    const tipoCampo = document.getElementById("tipoCampo").value;
    const cantidad = document.getElementById("cantidadCampo").value;
    
    const precioPorCampo = precios[nombreCampo][tipoCampo];
    const total = precioPorCampo * cantidad;
    
    document.getElementById("precioCampo").value = "$" + precioPorCampo.toFixed(2);
    document.getElementById("precioTotal").innerText = "$" + total.toFixed(2);
}

function procesarPago() {
    // Mostrar indicador de carga
    document.getElementById("loadingIndicator").style.display = "block";
    
    // Simular un proceso de pago (3 segundos)
    setTimeout(function() {
        document.getElementById("loadingIndicator").style.display = "none";
        mostrarConfirmacion();
    }, 1500);
}

function mostrarConfirmacion() {
    const nombreCampo = document.getElementById("nombreCampo").value;
    const tipoCampo = document.getElementById("tipoCampo").value;
    const cantidad = document.getElementById("cantidadCampo").value;
    const total = document.getElementById("precioTotal").innerText;
    
    // Actualizar la información en el modal
    document.getElementById("modal-campo").innerText = "Campo " + nombreCampo;
    document.getElementById("modal-tipo").innerText = tipoCampo;
    document.getElementById("modal-cantidad").innerText = cantidad;
    document.getElementById("modal-total").innerText = total;
    
    // Mostrar el modal
    document.getElementById("modalConfirmacion").style.display = "block";
}

function cerrarModal() {
    document.getElementById("modalConfirmacion").style.display = "none";
}

function volverInicio() {
    window.location.href = "{{ url_for('templates', filename='inicio.html') }}"
    alert("Redireccionar a página principal");
}

// Inicializar precios al cargar
window.onload = function() {
    actualizarPrecio();
};

// Cerrar el modal si se hace clic fuera del contenido
window.onclick = function(event) {
    const modal = document.getElementById("modalConfirmacion");
    if (event.target == modal) {
        cerrarModal();
    }
};
