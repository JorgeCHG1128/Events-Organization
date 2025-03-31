document.addEventListener('DOMContentLoaded', () => {
    // =================== FUNCIONALIDAD DE REGISTRO ===================
    const toggleHostFields = () => {
        const roleSelect = document.getElementById('role');
        const hostFields = document.getElementById('hostFields');
        
        if (roleSelect && hostFields) {
            const updateVisibility = () => {
                const isHost = roleSelect.value === 'host';
                hostFields.classList.toggle('hidden', !isHost);
                
                // Hacer campos requeridos solo si son visibles
                document.getElementById('companyName').required = isHost;
                document.getElementById('hostName').required = isHost;
            };
            
            updateVisibility(); // Estado inicial
            roleSelect.addEventListener('change', updateVisibility);
        }
    };

    const setupRegistrationForm = () => {
        const registerForm = document.getElementById('registerForm');
        const passwordInput = document.getElementById('password');
        const passwordFeedback = document.getElementById('passwordFeedback');

        if (!registerForm) return;

        passwordInput.addEventListener('input', () => {
            const password = passwordInput.value;
            const feedback = checkPasswordStrength(password);
            passwordFeedback.textContent = feedback.message;
            passwordFeedback.style.color = feedback.isValid ? 'green' : '#ff4d4d';
        });

        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearMessages();

            const formData = {
                name: document.getElementById('name').value.trim(),
                email: document.getElementById('email').value.trim(),
                password: document.getElementById('password').value.trim(),
                confirmPassword: document.getElementById('confirmPassword').value.trim(),
                role: document.getElementById('role').value,
                companyName: document.getElementById('companyName')?.value.trim(),
                hostName: document.getElementById('hostName')?.value.trim()
            };

            if (!validateRegistration(formData)) return;

            try {
                const response = await fetch('/registro', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.message || 'Error en el registro');
                }

                showMessage(data.message, 'success');
                setTimeout(() => window.location.href = data.redirect, 1500);
            } catch (error) {
                showMessage(error.message, 'error');
            }
        });
    };

    // =================== FUNCIONALIDAD DE LOGIN ===================
    const setupLoginForm = () => {
        const loginForm = document.getElementById('loginForm');
        if (!loginForm) return;

        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearMessages();

            const formData = {
                email: document.getElementById('email').value.trim(),
                password: document.getElementById('password').value.trim()
            };

            if (!validateLogin(formData)) return;

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.message || 'Credenciales inválidas');
                }

                // Redirección basada en el rol del usuario
                window.location.href = data.redirect || '/';
            } catch (error) {
                showMessage(error.message, 'error');
            }
        });
    };

    // =================== VALIDACIONES ===================
    const validateRegistration = (formData) => {
        // Validación de email
        if (!/^[\w.-]+@[\w.-]+\.\w+$/.test(formData.email)) {
            showMessage('Formato de email inválido', 'error');
            return false;
        }

        // Validación de contraseña
        const passwordCheck = checkPasswordStrength(formData.password);
        if (!passwordCheck.isValid) {
            showMessage(passwordCheck.message, 'error');
            return false;
        }

        // Validación de confirmación de contraseña
        if (formData.password !== formData.confirmPassword) {
            showMessage('Las contraseñas no coinciden', 'error');
            return false;
        }

        // Validación de campos de host
        if (formData.role === 'host' && (!formData.companyName || !formData.hostName)) {
            showMessage('Completa todos los campos de organizador', 'error');
            return false;
        }

        return true;
    };

    const validateLogin = (formData) => {
        if (!formData.email || !formData.password) {
            showMessage('Todos los campos son requeridos', 'error');
            return false;
        }
        return true;
    };

    // =================== HELPERS ===================
    const showMessage = (message, type) => {
        const container = document.getElementById('messageContainer');
        if (!container) return;

        container.innerHTML = `
            <div class="message ${type}">
                ${message}
            </div>
        `;
        container.style.display = 'block';
        
        setTimeout(() => {
            container.style.display = 'none';
        }, 5000);
    };

    const clearMessages = () => {
        const container = document.getElementById('messageContainer');
        if (container) container.style.display = 'none';
    };

    // =================== FUNCIONES AUXILIARES ===================
    function checkPasswordStrength(password) {
        const validations = {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            number: /\d/.test(password),
            specialChar: /[!@#$%^&*(),.?\":{}|<>]/.test(password)
        };

        const messages = [];
        if (!validations.length) messages.push('Mínimo 8 caracteres');
        if (!validations.uppercase) messages.push('Al menos una mayúscula');
        if (!validations.number) messages.push('Al menos un número');
        if (!validations.specialChar) messages.push('Al menos un carácter especial');

        return {
            isValid: Object.values(validations).every(v => v),
            message: messages.join(', ') || 'Contraseña segura ✅'
        };
    }

    function showError(message) {
        const errorDiv = document.getElementById('errorMessage');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }

    function showSuccess(message) {
        const successDiv = document.getElementById('successMessage');
        successDiv.textContent = message;
        successDiv.style.display = 'block';
    }

    // =================== INICIALIZACIÓN ===================
    toggleHostFields(); // Para el formulario de registro
    setupRegistrationForm();
    setupLoginForm();

    // =================== AGREGADO: Redirección al formulario de registro ===================
    document.getElementById("registerButton")?.addEventListener("click", function () {
        window.location.href = "/registro";
    });

});
