import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

class Emailer():
    def __init__(self):
        self.smtp_server = 'smtp.gmail.com'  # Reemplaza con tu servidor SMTP
        self.smtp_port = 587  # El puerto puede variar según el servidor
        self.smtp_username = 'nicovy3107@gmail.com'  # Tu dirección de correo electrónico
        self.smtp_password = 'inpz tybg bpkq rbof'  # Tu contraseña de aplicación

    def sendmail(self, content, from_email="Test From", to_email="Test To", subject="Test subject"):
        from_name = 'Universidad ORT Uruguay'
        from_email = 'noreply@ort.edu.uy'
        to_email = 'nicovy3107@gmail.com'
        subject = 'Alerta por dado de baja de Universidad ORT'

        # Crea el objeto MIMEMultipart
        msg = MIMEMultipart()
        msg['From'] = formataddr((from_name, from_email))
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
