function openAadJumpsModal() {
    $('#newRigModal').modal('hide');
    $('#aadJumpsModal').modal('show');
}

function submitForm() {
    const currentAadJumps = document.getElementById('current_aad_jumps').value;
    const form = document.getElementById('newRigForm');
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'current_aad_jumps';
    input.value = currentAadJumps;
    form.appendChild(input);
    $('#aadJumpsModal').modal('hide');
    form.submit();
}

document.addEventListener("DOMContentLoaded", function () {
    // Verificar si la URL actual corresponde a la pestaña "Rigs"
    if (window.location.pathname === '/rigs') {
        // Agregar evento de clic a cada fila de la tabla de rigs
        document.querySelectorAll('.full-width-table-rig tbody tr').forEach(row => {
            row.addEventListener('click', function () {
                // Redirige a la página del rig
                const rigId = row.getAttribute('data-id');
                window.location.href = `/rig/${rigId}`;
            });
        });
    } else if (window.location.pathname.includes('/rigging')) {
        // Agregar evento de clic a cada fila de la tabla de rigging
        document.querySelectorAll('.full-width-table-rigging tbody tr').forEach(row => {
            row.addEventListener('click', function () {
                // Redirige a la página de detalles de rigging
                const riggingId = row.getAttribute('data-id');
                window.location.href = `/rigging/${riggingId}`;
            });
        });
    } else {
        // Agregar evento de clic a cada fila de la tabla de componentes
        document.querySelectorAll('.full-width-table tbody tr').forEach(row => {
            row.addEventListener('click', function () {
                // Redirige a la página del componente
                const componentId = row.getAttribute('data-id');
                window.location.href = `/component/show/${componentId}`;
            });
        });
    }
});


function validateAndSubmitForm(componentId) {
    const currentAadJumpsInput = document.getElementById(`current_aad_jumps-${componentId}`);
    const aadJumpsOnMountInput = document.getElementById(`aad_jumps_on_mount-${componentId}`);
    const errorMessageDiv = document.getElementById(`error-message-${componentId}`);

    if (!currentAadJumpsInput || !aadJumpsOnMountInput || !errorMessageDiv) {
        console.error('Element not found!');
        return false;
    }

    const currentAadJumps = parseInt(currentAadJumpsInput.value, 10);
    const aadJumpsOnMount = parseInt(aadJumpsOnMountInput.value, 10);

    if (isNaN(currentAadJumps) || isNaN(aadJumpsOnMount)) {
        errorMessageDiv.textContent = 'Both Current AAD Jumps and AAD Jumps on Mount must be integers';
        return false; // Impide el envío del formulario si la validación falla
    }

    if (currentAadJumps < aadJumpsOnMount) {
        errorMessageDiv.textContent = 'Current AAD Jumps cannot be less than AAD Jumps on Mount';
        return false; // Impide el envío del formulario si la validación falla
    } else {
        return true; // Permite el envío del formulario si la validación pasa
    }
}

document.addEventListener('DOMContentLoaded', function () {
    $('.modal').on('shown.bs.modal', function (event) {
        const button = $(event.relatedTarget); // Botón que activó el modal
        const componentId = button.data('component-id'); // Extraer información de los atributos data-*
        const modal = $(this);

        modal.find('.btn-danger').off('click').on('click', function () {
            const form = document.getElementById(`removeComponentForm-${componentId}`);
            if (validateAndSubmitForm(componentId)) {
                form.submit();
            }
        });
    });
});


function setupClickableRows() {
    // Asigna el evento clic a las filas de la tabla
    $('.clickable-row').off('click').on('click', function () {
        const id = $(this).data('id');       // ID de la fila
        const type = $(this).data('type');   // Tipo (rig, component, rigging)

        if (id && type) {
            // Redirige según el tipo de contenido
            switch (type) {
                case 'rig':
                    window.location.href = `/rig/${id}`;
                    break;
                case 'component':
                    window.location.href = `/component/show/${id}`;
                    break;
                case 'rigging':
                    window.location.href = `/rigging/${id}`;
                    break;
                default:
                    console.error(`Tipo desconocido: ${type}`);
            }
        } else {
            console.error('Falta el atributo data-id o data-type en la fila');
        }
    });
}


$(document).ready(function () {
    // Configura el clic para el enlace "Rigs"
    $('#rigs-link').click(function (event) {
        event.preventDefault(); // Evita la recarga de la página

        $.ajax({
            url: '/rigs', // Ruta que deseas cargar
            type: 'GET',
            success: function (data) {
                // Extrae y reemplaza solo el bloque principal
                const content = $(data).find('#main-content').html();
                $('#main-content').html(content);

                // Actualiza la URL sin recargar la página
                history.pushState(null, '', '/rigs');

                // Reasigna los eventos de clic a las filas
                setupClickableRows();
            },
            error: function (xhr, status, error) {
                console.error('Error al cargar /rigs:', error);
            }
        });
    });

    // Maneja el botón de "Atrás" y "Adelante" del navegador
    window.addEventListener('popstate', function () {
        $.ajax({
            url: window.location.pathname,
            type: 'GET',
            success: function (data) {
                const content = $(data).find('#main-content').html();
                $('#main-content').html(content);

                // Reasigna los eventos de clic a las filas
                setupClickableRows();
            },
            error: function (xhr, status, error) {
                console.error('Error al manejar popstate:', error);
            }
        });
    });

    // Configura los clics al cargar la página
    setupClickableRows();
});