function setupClickableComponentRows() {
    $(document).off('click', '.clickable-row').on('click', '.clickable-row', function (event) {
        event.preventDefault(); // Evita la navegación normal

        const componentId = $(this).data('id');  // ID del componente
        if (componentId) {
            $.ajax({
                url: `/component/show/${componentId}`,  // Ruta a los detalles del componente
                type: 'GET',
                success: function (data) {
                    // Extrae y reemplaza el contenido del #main-content
                    const content = $(data).find('#main-content').html();
                    $('#main-content').html(content);

                    // Actualiza la URL en la barra de direcciones sin recargar
                    history.pushState(null, '', `/component/show/${componentId}`);

                    // Reasigna eventos si hay elementos interactivos en la nueva vista
                    setupBackToComponents();
                },
                error: function (xhr, status, error) {
                    console.error(`Error al cargar el componente ${componentId}:`, error);
                }
            });
        } else {
            console.error('No se encontró el atributo data-id en la fila');
        }
    });
}

function setupBackToComponents() {
    $(document).off('click', '#back-to-components').on('click', '#back-to-components', function (event) {
        event.preventDefault();

        $.ajax({
            url: '/components',
            type: 'GET',
            success: function (data) {
                const content = $(data).find('#main-content').html();
                $('#main-content').html(content);

                // Actualiza la URL en la barra de direcciones
                history.pushState(null, '', '/components');

                // Reasigna los eventos de clic a las filas de la tabla
                setupClickableComponentRows();
            },
            error: function (xhr, status, error) {
                console.error('Error al cargar /components:', error);
            }
        });
    });
}

$(document).ready(function () {
    console.log("Archivo components.js cargado.");

    $('#components-link').click(function (event) {
        event.preventDefault(); // Evita la recarga de la página

        $.ajax({
            url: '/components',
            type: 'GET',
            success: function (data) {
                const content = $(data).find('#main-content').html();
                $('#main-content').html(content);

                history.pushState(null, '', '/components');

                setupClickableComponentRows();
            },
            error: function (xhr, status, error) {
                console.error('Error al cargar /components:', error);
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
                setupClickableComponentRows();
            },
            error: function (xhr, status, error) {
                console.error('Error al manejar popstate:', error);
            }
        });
    });

    setupClickableComponentRows();
});
