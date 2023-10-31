// script.js

$(document).ready(function() {
    var claveSecreta = "{{ clave_secreta }}";

    // Obtén el elemento de nombre de usuario y el enlace de cierre de sesión
    var userNameElement = document.getElementById("user-name");
    var logoutLink = document.getElementById("logout-link");

    // Agrega un evento de clic al enlace de cierre de sesión
    logoutLink.addEventListener("click", function(event) {
        event.preventDefault(); // Evita que el enlace navegue a la página de cierre de sesión
        // Realiza una solicitud para cerrar la sesión
        $.ajax({
            type: "GET",
            url: "/logout",
            success: function(response) {
                // Redirige o realiza otras acciones necesarias después del cierre de sesión
                window.location.href = "/"; // Redirige a la página de inicio, por ejemplo
            },
            error: function(error) {
                console.error("Error al cerrar la sesión: " + JSON.stringify(error));
            }
        });
    });

    // Función para cargar y mostrar los usuarios
    function loadAndShowUsers() {
        $.ajax({
            type: "GET",
            url: "/users/list",
            headers: {
                'X-App-Header': claveSecreta
            },
            success: function(users) {
                // Borra la lista existente
                $("#user-list").empty();

                // Agrega los usuarios a la lista
                users.forEach(function(user) {
                    var listItem = $("<li>").text(user);
                    $("#user-list").append(listItem);
                });
            },
            error: function(error) {
                console.error("Error al obtener la lista de usuarios: " + JSON.stringify(error));
            }
        });
    }

    $("#manage-users-button").click(function() {
        loadAndShowUsers(); // Carga y muestra la lista de usuarios
        $("#user-modal").css("display", "block"); // Abre el cuadro de diálogo modal
        $("#error-message").css("display", "none");
        $("#user-email").text("");
    });

    $("#add-user-button").click(function() {
        var userEmail = $("#user-email").val();
        var emailFormat = /\S+@\S+\.\S+/;
        if (!emailFormat.test(userEmail)) {
            $("#error-message").text("Formato de correo electrónico no válido").css("color", "red").css("display", "block");
            return;
        }

        //var newPassword = generateRandomPassword(8);
        var newPassword = "{{ contrasenaSecreta }}";
        var newUser = { username: userEmail, password: newPassword };

        // Realizar una solicitud POST para agregar el nuevo usuario
        $.ajax({
            type: "POST",
            url: "/users/add",  // Debes definir esta ruta en tu aplicación Flask
            data: JSON.stringify(newUser),
            contentType: "application/json",
            headers: { 'X-App-Header': claveSecreta },
            success: function(response) {
                // La respuesta puede contener información adicional, si es necesario
                $("#error-message").text(response.message).css("color", response.color).css("display", "block");
                loadAndShowUsers();  // Actualiza la lista de usuarios después de agregar uno nuevo
            },
            error: function(error) {
                console.error("Error al agregar el usuario: " + JSON.stringify(error));
                $("#error-message").text("Hubo un error al agregar el usuario").css("color", "red").css("display", "block");
            }
        });
    });

    $("#delete-user-button").click(function() {
        var userEmail = $("#user-email").val(); // Obtén el email del usuario que se desea borrar
        var emailFormat = /\S+@\S+\.\S+/;
        if (!emailFormat.test(userEmail)) {
            $("#error-message").text("Formato de correo electrónico no válido").css("color", "red").css("display", "block");
            return;
        }
        // Realiza una solicitud DELETE al servidor para borrar el usuario
        $.ajax({
            type: "DELETE",
            url: "/users/delete",  // Debes definir esta ruta en tu aplicación Flask
            data: JSON.stringify({ username: userEmail }), // Envía el email del usuario a borrar
            contentType: "application/json",
            headers: { 'X-App-Header': claveSecreta },
            success: function(response) {
                // La respuesta puede contener información adicional, si es necesario
                $("#error-message").text(response.message).css("color", response.color).css("display", "block");
                loadAndShowUsers();  // Actualiza la lista de usuarios después de borrar uno
            },
            error: function(error) {
                console.error("Error al borrar el usuario: " + JSON.stringify(error));
                $("#error-message").text("Hubo un error al borrar el usuario").css("color", "red").css("display", "block");
            }
        });
    });

    $("#reload-model-button").click(function() {
        $("#loading-overlay").css("display", "flex");
        $.ajax({
            type: "GET",
            header: {
                'X-App-Header': claveSecreta
            },
            url: "/reload_model",
            success: function(response) {
                // Puedes manejar la respuesta si es necesario
                console.log("Model reloaded successfully");
                $(".video-container .model-text").text(response.modelName);
                $("#loading-overlay").css("display", "none");
            },
            error: function(error) {
                console.error("Error al recargar el modelo: " + JSON.stringify(error));
                $("#loading-overlay").css("display", "none");
            }
        });
    });

    $("#change-models-folder-button").click(function() {
        $("#change-models-folder-modal").css("display", "block");
        $("#info-message").css("display", "none");
        $("#models-folder-url").text("");
    });

    $("#confirm-models-folder-button").click(function() {
        // Aquí puedes capturar la URL de Google Drive ingresada en el cuadro de texto y realizar las acciones necesarias.
        var modelsFolderURL = $("#models-folder-url").val();
        var regexPattern = /folders\/([a-zA-Z0-9-_]+)/;
        var match = modelsFolderURL.match(regexPattern);
        if(match){
            var folderId = match[1];  // El ID del folder estará en el primer grupo capturado por los paréntesis
            console.log("Folder ID:", folderId);
            $.ajax({
                type: "POST",  // Ajusta el método HTTP según tu implementación en Flask
                url: "/model/change_folder",  // Ajusta la ruta de tu endpoint en Flask
                data: { folder_id: folderId },  // Envía el folderId como dato
                success: function(response) {
                    // Puedes manejar la respuesta si es necesario
                    console.log("Folder changed successfully");
                    $("#info-message").text('Ahora debes hacer click en "Reload Model" para descargar el último modelo disponible').css("color", "green").css("display", "block");
                },
                error: function(error) {
                    console.error("Error al cambiar el folder: " + JSON.stringify(error));
                    $("#info-message").text("Error al cambiar el folder: " + JSON.stringify(error)).css("color", "red").css("display", "block");
                }
            });
        } else {
            $("#info-message").text("No se encontró el Folder ID en la URL.").css("color", "red").css("display", "block");
        }
        // Luego puedes ocultar el pop-up modal
        // $("#change-models-folder-modal").css("display", "none");
    });

    // Captura el clic en el botón "Show Recordings" para cargar y mostrar las grabaciones de video
    $("#show-recordings-button").click(function() {
        // Realiza una solicitud AJAX para obtener la lista de grabaciones
        $.ajax({
            type: "GET",
            url: "/recordings/list", // Ajusta la ruta de tu endpoint en Flask para obtener la lista de grabaciones
            success: function(response) {
                // Maneja la respuesta para mostrar la lista de grabaciones en un pop-up
                // Puedes usar JavaScript para construir elementos HTML y mostrarlos en un pop-up modal
                console.log("Lista de grabaciones:", response);

                // Por cada grabación en la respuesta, crea elementos HTML para mostrar la grabación
                response.forEach(function(recording) {
                    var recordingDiv = $("<div class='recording-item'></div>");
                    var thumbnailImg = $("<img src='" + recording.thumbnail_path + "' class='thumbnail' />");
                    var name = $("<p>" + recording.name + "</p>");
                    var playButton = $("<button class='play-button' data-video='" + recording.video_path + "'>Play</button>");
                    var sendMailButton = $("<button class='send-mail-button' data-video='" + recording.video_path + "'>Send Mail</button>");
                    var deleteButton = $("<button class='delete-button' data-video='" + recording.video_path + "'>Delete</button>");

                    recordingDiv.append(thumbnailImg, name, playButton, sendMailButton, deleteButton);

                    // Agrega el elemento al pop-up modal
                    $("#recordings-popup").append(recordingDiv);

                    // Asigna funciones a los botones (puedes definir estas funciones)
                    playButton.click(function() {
                        var videoPath = $(this).data("video");
                        // Agrega código para reproducir el video
                    });

                    sendMailButton.click(function() {
                        var videoPath = $(this).data("video");
                        // Agrega código para enviar el video por correo
                    });

                    deleteButton.click(function() {
                        var videoPath = $(this).data("video");
                        // Agrega código para eliminar la grabación
                    });
                });

                // Muestra el pop-up modal
                $("#recordings-modal").css("display", "block");
            },
            error: function(error) {
                console.error("Error al obtener la lista de grabaciones: " + JSON.stringify(error));
            }
        });
    });

    // Cierra el cuadro de diálogo haciendo clic fuera de él
    $(window).click(function (event) {
        if (event.target === document.getElementById('user-modal')) {
            $("#user-modal").css("display", "none");
        }
        if (event.target === document.getElementById('change-models-folder-modal')) {
            $("#change-models-folder-modal").css("display", "none");
        }

    });


});
