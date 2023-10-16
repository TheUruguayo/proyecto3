// script.js

$(document).ready(function() {
    // Ejemplo de datos de usuarios en un array
    var usersData = [
        {"username": "email1@ejemplo.com", "role": "Admin"},
        {"username": "email2@ejemplo.com", "role": "User"}
        // Puedes agregar más usuarios aquí
    ];

    // Función para generar la lista de usuarios
    function generateUserList() {
        var userList = $("#user-list");
        userList.empty(); // Limpia la lista existente
        for (var i = 0; i < usersData.length; i++) {
            var userData = usersData[i];
            var listItem = $("<li>").text(userData.username + " - " + userData.role);
            userList.append(listItem);
        }
    }

    // Función para cargar y mostrar las grabaciones de video
    function loadAndShowRecordings() {
        $.ajax({
            type: "GET",
            url: "/get_recordings",
            success: function(response) {
                // Mostrar las grabaciones de video en la sección correspondiente
                $("#video-recordings").html(response);
                $("#video-recordings").slideDown(); // Mostrar la sección con animación de deslizamiento
            },
            error: function(error) {
                console.error("Error al obtener las grabaciones de video: " + JSON.stringify(error));
            }
        });
    }

    function updateVideoFrame() {
        // Realiza una petición AJAX para obtener el último frame generado
        $.ajax({
            url: '/video_frame_data',  // Ruta para obtener los frames
            cache: false, // Evitar la caché del navegador
            success: function (data) {
                $('#video-frame').attr('src', 'data:image/jpeg;base64,' + data);
                updateVideoFrame(); // Actualizar de nuevo
            },
        });
    }

    updateVideoFrame(); // Comienza la actualización del marco de video

    // Captura el clic en el botón "Manage Users" para abrir el cuadro de diálogo modal y generar la lista
    $("#manage-users-button").click(function() {
        generateUserList();
        $("#user-modal").css("display", "block");
    });

    // Captura el clic en el botón "Show Recordings" para cargar y mostrar las grabaciones de video
    $("#show-recordings-button").click(function() {
        loadAndShowRecordings();
    });

    // Captura el clic en el botón "Manage Users" para abrir el cuadro de diálogo modal y generar la lista
    $("#manage-users-button").click(function () {
        generateUserList();
        $("#user-modal").css("display", "block");
    });

    // Captura el clic en el botón de cierre
    $("#close-modal-button").click(function () {
        $("#user-modal").css("display", "none");
    });

    // Cierra el cuadro de diálogo haciendo clic fuera de él
    $(window).click(function (event) {
        if (event.target == document.getElementById('user-modal')) {
            $("#user-modal").css("display", "none");
        }
    });
});
