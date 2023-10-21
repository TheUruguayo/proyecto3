import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from dotenv import load_dotenv, find_dotenv


class Emailer():
    def __init__(self):
        load_dotenv(find_dotenv())
        self.smtp_server = os.getenv("EMAILER-SERVER")  # Reemplaza con tu servidor SMTP
        self.smtp_port = int(os.getenv("EMAILER-PORT"))  # El puerto puede variar según el servidor
        self.smtp_username = os.getenv("EMAILER-USERNAME")  # Tu dirección de correo electrónico
        self.smtp_password = os.getenv("EMAILER-PASSWORD")  # Tu contraseña de aplicación

    def sendmail(self, content, from_name = "Test Name", from_email="Test From", to_email="Test To", subject="Test subject"):
        msg = MIMEMultipart()
        if subject == "start_ngrok":
            from_name = 'My Personal Spy Cam'
            # from_email = 'noreply@gmail.uy'
            to_email = self.smtp_username
            subject = 'My Personal Spy Cam'

            msg['From'] = formataddr((from_name, self.smtp_username))
            msg['To'] = to_email
            msg['Subject'] = subject

            # Contenido HTML del correo electrónico
            html_content = f"""
                    <html>
                    <head></head>
                    <body>
                        <p>Esta es la URL para camera server: {content}</p>
                    </body>
                    </html>
                    """
            msg.attach(MIMEText(html_content, 'html'))
        elif subject == "add_user":
            print(content)
            from_name = 'My Personal Spy Cam'
            # to_email = self.smtp_username
            subject = 'New User Added'

            msg['From'] = formataddr((from_name, self.smtp_username))
            msg['To'] = to_email
            msg['Subject'] = subject

            # Contenido HTML del correo electrónico
            html_content = f"""
            <html>
            <head></head>
            <body>
                <p>Se ha agregado correctamente el usuario {to_email} a My Personal Spy Cam! <br> 
                    Ahora debes entrar a {content["url"]} e ingresarás con la contraseña "{content["password"]}". <br> 
                    Cuando ingreses, te pedirá cambiar la contraseña automáticamente. <br>
                    Muchas gracias!<br>
                    My Personal Spy Cam
                </p>
            </body>
            </html>
            """
            msg.attach(MIMEText(html_content, 'html'))

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Inicia la conexión TLS para cifrar la comunicación
            server.login(self.smtp_username, self.smtp_password)

            # Envía el mensaje de correo electrónico
            server.sendmail(from_email, to_email, msg.as_string())

            # Cierra la conexión al servidor SMTP
            server.quit()

            print('El correo electrónico se envió exitosamente.')
        except Exception as e:
            print(f'Error al enviar el correo electrónico: {str(e)}')
