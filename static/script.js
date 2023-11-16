$(document).ready(function() {
            var claveSecreta = "{{ clave_secreta }}";

            // Obtén el elemento de nombre de usuario y el enlace de cierre de sesión
            var userNameElement = document.getElementById("user-name");
            var logoutLink = document.getElementById("logout-link");

            $("#video-player").hide();

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
                        console.log(response);
                        var recordingsDiv = $("#recordings-popup .recordings-list");
                        recordingsDiv.empty();

                        // Por cada grabación en la respuesta, crea elementos HTML para mostrar la grabación
                        response.forEach(function(recording) {
                            /*
                            * 0: id interno (no me interesa)
                            * 1: nombre del video "video-time.time"
                            * 2: video path (abs)
                            * 3: thumbnail path
                            * 4: created at
                            */

                            var recordingItemDiv = $("<div class='recording-item'></div>");
                            var recordingInfoDiv = $("<div class='recording-info'></div>");
                            var thumbnail = $("<img class='recording-thumbnail' src='/thumbnails/" + encodeURIComponent(recording[3].replace(/\\/g, '/')) + "'>");
                            var name = $("<p class='recording-name centered'>" + recording[4] + "</p>");
                            var buttonContainer = $("<div class='recordings-button-container'></div>");
                            var downloadButton = $("<button class='download-button' data-video='" + recording[2] + "'>Download</button>")
                            var deleteButton = $("<button class='delete-button' data-video='" + recording[2] + "'>Delete</button>");

                            buttonContainer.append(downloadButton, deleteButton);
                            recordingInfoDiv.append(thumbnail, name, buttonContainer);
                            recordingItemDiv.append(thumbnail, name, buttonContainer);

                            recordingsDiv.append(recordingItemDiv);


                            // Agrega una línea separadora después de cada grabación (excepto la última)
                            if (response.indexOf(recording) < response.length - 1) {
                                var separator = $("<hr class='recording-separator'>");
                                recordingsDiv.append(separator);
                            }
                            // Asigna funciones a los botones (puedes definir estas funciones)
                            downloadButton.click(function() {
                                var videoPath = $(this).data("video");
                                var parts = videoPath.split("/");
                                var relPath = parts[parts.length - 3] + '/' + parts[parts.length - 2] + '/' + parts[parts.length - 1];

                                // Realiza una solicitud fetch para obtener el video
                                fetch("/play_video/" + relPath)
                                    .then(response => response.blob())
                                    .then(blob => {
                                        // Crea un objeto URL para el Blob
                                        var videoUrl = URL.createObjectURL(blob);

                                        // Crea un enlace temporal para la descarga
                                        var downloadLink = document.createElement('a');
                                        downloadLink.href = videoUrl;
                                        downloadLink.download = parts[parts.length - 1];  // Puedes establecer el nombre del archivo aquí

                                        // Añade el enlace al cuerpo del documento y simula un clic en él
                                        document.body.appendChild(downloadLink);
                                        downloadLink.click();

                                        // Elimina el enlace después de la descarga
                                        document.body.removeChild(downloadLink);

                                        // Reproduce el video
                                        var videoPlayer = document.getElementById("video-player");
                                        videoPlayer.src = videoUrl;
                                        videoPlayer.play();
                                    })
                                    .catch(error => console.error('Error al obtener el video:', error));
                            });

                            deleteButton.click(function() {
                                var videoPath = $(this).data("video");
                                var parts = videoPath.split("/");
                                var relPath = parts[parts.length - 3] + '/' + parts[parts.length - 2] + '/' + parts[parts.length - 1];

                                fetch("/delete_video/" + videoPath, {
                                    method: 'DELETE'
                                })
                                .then(response => response.json())
                                .then(data => {
                                    if (data.success) {
                                        console.log(data.message);
                                        $("#recordings-popup").css("display", "none");
                                        alert(data.message);
                                    } else {
                                        console.error(data.message);
                                    }
                                })
                                .catch(error => console.error('Error al eliminar el video:', error));
                            });
                        });

                        // Muestra el pop-up modal
                        $("#recordings-popup").css("display", "block");
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
                if (event.target === document.getElementById('recordings-popup')) {
                    $("#recordings-popup").css("display", "none");

                }
            });


        });