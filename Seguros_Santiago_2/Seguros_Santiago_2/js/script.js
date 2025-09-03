// Validaciones del lado del cliente
document.addEventListener('DOMContentLoaded', function() {
    // Validar formularios antes de enviar
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = 'red';
                } else {
                    field.style.borderColor = '';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Por favor, complete todos los campos requeridos.');
            }
        });
    });

    // Validar RUT en tiempo real
    const rutInputs = document.querySelectorAll('input[name="rut"]');
    rutInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\./g, '').replace('-', '');
            
            if (value.length > 0) {
                value = value.slice(0, -1) + '-' + value.slice(-1);
            }
            
            if (value.length > 2) {
                value = value.slice(0, -2).replace(/\B(?=(\d{3})+(?!\d))/g, '.') + value.slice(-2);
            }
            
            e.target.value = value;
        });
    });

    // Validar números en campos económicos
    const economicInputs = document.querySelectorAll('input[type="number"]');
    economicInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            if (e.target.value < 0) {
                e.target.value = 0;
            }
        });
    });

    // Mostrar/ocultar mensajes de alerta
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Confirmar eliminaciones
    const deleteButtons = document.querySelectorAll('button[type="submit"].btn-danger');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('¿Está seguro de que desea eliminar este registro? Esta acción no se puede deshacer.')) {
                e.preventDefault();
            }
        });
    });
});

// Función para formatear moneda
function formatCurrency(value) {
    return new Intl.NumberFormat('es-CL', {
        style: 'currency',
        currency: 'CLP'
    }).format(value);
}

// Función para validar email
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Función para validar teléfono
function isValidPhone(phone) {
    const phoneRegex = /^\+?[\d\s\-\(\)]{8,}$/;
    return phoneRegex.test(phone);
}
