// Función para previsualizar la imagen
function previewImage() {
    const fileInput = document.getElementById('profileImage');
    const preview = document.getElementById('imagePreview');
    
    if (fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            currentImage = e.target.result;
        };
        reader.readAsDataURL(fileInput.files[0]);
    }
}
