$(document).ready(function () {
    $(".dynamic-link").click(function (event) {
        event.preventDefault(); // Evita la recarga de la página

        let url = $(this).attr("href");

        // Animación de carga
        $("#main-content").fadeOut(200, function () {
            $("#preloader").fadeIn(200);
        });

        $.ajax({
            url: url,
            type: "GET",
            success: function (data) {
                // Reemplaza el contenido después de cargar
                let newContent = $(data).find("#main-content").html();
                $("#main-content").html(newContent);

                // Cambia la URL sin recargar la página
                history.pushState(null, "", url);

                // Oculta el preloader y muestra el nuevo contenido suavemente
                $("#preloader").fadeOut(200, function () {
                    $("#main-content").fadeIn(200);
                });

                // Reasigna eventos a filas clickeables en cada página nueva
                setupClickableRows();
                setupClickableComponentRows();
            },
            error: function (xhr, status, error) {
                console.error("Error al cargar:", error);
            }
        });
    });

    // Maneja el botón de "Atrás" y "Adelante" del navegador
    window.addEventListener("popstate", function () {
        $.ajax({
            url: window.location.pathname,
            type: "GET",
            success: function (data) {
                let newContent = $(data).find("#main-content").html();
                $("#main-content").html(newContent);

                $("#preloader").fadeOut(200, function () {
                    $("#main-content").fadeIn(200);
                });

                setupClickableRows();
                setupClickableComponentRows();
            },
            error: function (xhr, status, error) {
                console.error("Error al manejar popstate:", error);
            }
        });
    });
});
