function setupClickableRows() {
    $(document).off('click', '.clickable-row').on('click', '.clickable-row', function (event) {
        event.preventDefault(); // Evita la navegación normal

        const id = $(this).data('id');  // ID del rig
        if (id) {
            $.ajax({
                url: `/rig/${id}`,  // Llamada a la API o vista de detalles del rig
                type: 'GET',
                success: function (data) {
                    // Extrae el contenido de #main-content desde la respuesta y reemplaza el actual
                    const content = $(data).find('#main-content').html();
                    $('#main-content').html(content);

                    // Actualiza la URL sin recargar la página
                    history.pushState(null, '', `/rig/${id}`);

                    // Vuelve a asignar eventos si hay elementos interactivos en la nueva vista
                    setupBackToRigs();
                },
                error: function (xhr, status, error) {
                    console.error(`Error al cargar el Rig ${id}:`, error);
                }
            });
        } else {
            console.error('No se encontró el atributo data-id en la fila');
        }
    });
}

function setupBackToRigs() {
    $(document).off('click', '#back-to-rigs').on('click', '#back-to-rigs', function (event) {
        event.preventDefault();

        $.ajax({
            url: '/rigs',
            type: 'GET',
            success: function (data) {
                const content = $(data).find('#main-content').html();
                $('#main-content').html(content);

                // Actualiza la URL en la barra de direcciones
                history.pushState(null, '', '/rigs');

                // Reasigna los eventos de clic a las filas de la tabla
                setupClickableRows();
            },
            error: function (xhr, status, error) {
                console.error('Error al cargar /rigs:', error);
            }
        });
    });
}

$(document).ready(function () {
    console.log("Archivo rigs.js cargado.");

    $('#rigs-link').click(function (event) {
        event.preventDefault(); // Evita la recarga de la página

        $.ajax({
            url: '/rigs',
            type: 'GET',
            success: function (data) {
                const content = $(data).find('#main-content').html();
                $('#main-content').html(content);

                history.pushState(null, '', '/rigs');

                setupClickableRows();
            },
            error: function (xhr, status, error) {
                console.error('Error al cargar /rigs:', error);
            }
        });
    });

    window.addEventListener('popstate', function () {
        $.ajax({
            url: window.location.pathname,
            type: 'GET',
            success: function (data) {
                const content = $(data).find('#main-content').html();
                $('#main-content').html(content);

                // Reasigna los eventos de clic tras recargar contenido
                setupClickableRows();
            },
            error: function (xhr, status, error) {
                console.error('Error al manejar popstate:', error);
            }
        });
    });

    setupClickableRows();
});
