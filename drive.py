import pickle
import os.path
import time, re

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import io
from googleapiclient.http import MediaIoBaseDownload
from flask import Flask, redirect, session, request, render_template, Response, current_app, send_from_directory
import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
from requests_oauthlib import OAuth2Session
# from pyngrok import ngrok
import requests
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.utils import formataddr

# from pycoral.utils import edgetpu
# from pycoral.utils import dataset
# from pycoral.adapters import common
# from pycoral.adapters import classify

import tflite_runtime.interpreter as tf
# class DriveDownloader:
#     def __init__(self):
#         self.service = self.get_drive_service()
#
#     def get_drive_service(self):
#         creds = None
#
#         # The file token.pickle stores the user's access and refresh tokens,
#         # and is created automatically when the authorization flow completes for the first time.
#         try:
#             if os.path.exists('token.pickle'):
#                 with open('token.pickle', 'rb') as token:
#                     creds = pickle.load(token)
#         except:
#             if os.path.exists('home/pi/tmp/pycharm_project_377/token.pickle'):
#                 with open('home/pi/tmp/pycharm_project_377/token.pickle', 'rb') as token:
#                     creds = pickle.load(token)
#         # If there are no (valid) credentials available, prompt the user to log in.
#         if not creds or not creds.valid:
#             if creds and creds.expired and creds.refresh_token:
#                 creds.refresh(Request())
#             else:
#                 try:
#
#                     flow = InstalledAppFlow.from_client_secrets_file('credentials.json',
#                                                                      ['https://www.googleapis.com/auth/drive.readonly'])
#                 except:
#                     flow = InstalledAppFlow.from_client_secrets_file('home/pi/tmp/pycharm_project_377/credentials.json',
#                                                                      ['https://www.googleapis.com/auth/drive.readonly'])
#                 creds = flow.run_local_server(port=0)
#
#             # Save the credentials for the next run
#             try:
#                 with open('token.pickle', 'wb') as token:
#                     pickle.dump(creds, token)
#             except:
#                 with open('home/pi/tmp/pycharm_project_377/token.pickle', 'wb') as token:
#                     pickle.dump(creds, token)
#         return build('drive', 'v3', credentials=creds)
#
#     def _list_files_in_folder(self, folder_id):
#         query = f"'{folder_id}' in parents"
#         results = self.service.files().list(q=query, orderBy='createdTime desc', pageSize=1, fields="files(id, name, createdTime)").execute()
#         items = results.get('files', [])
#
#         if not items:
#             print('No files found.')
#             return None
#         else:
#             newest_file = items[0]
#             print(f"Newest file is: {newest_file['name']} (ID: {newest_file['id']}, Created: {newest_file['createdTime']})")
#             return newest_file
#
#     def _download_file(self, file_id, filename):
#         request = self.service.files().get_media(fileId=file_id)
#         fh = io.FileIO(filename, 'wb')
#         downloader = MediaIoBaseDownload(fh, request)
#
#         done = False
#         while not done:
#             status, done = downloader.next_chunk()
#             print(f"Downloaded {int(status.progress() * 100)}%")
#
#     def download_from_drive(self):
#         folder_id = "1Qm1u0i9Ck1nLsTR7EExIQSDPbSC3Ltsn"
#         newest_file = self._list_files_in_folder(folder_id)
#         if newest_file:
#             self._download_file(newest_file['id'], newest_file['name'])
#             return os.path.abspath(newest_file['name'])
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import secrets, jwt
from ngrok import ngrokTunnel
from emailer import Emailer
import socket
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connect to a known external IP address
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        return "localhost"

local_ip = get_local_ip()

API_KEY = 'AIzaSyD4E-EnfS8h0AlNlvKWzgBsRYqm0Sx32Mw'


# Modificar y agregar métodos de login a esta clase
class DriveDownloader:
    def __init__(self):
        self.service = self.get_drive_service()

    def get_drive_service(self):
        return build('drive', 'v3', developerKey=API_KEY)

    def _list_files_in_folder(self, folder_id):
        query = f"'{folder_id}' in parents"
        results = self.service.files().list(q=query, orderBy='createdTime desc', pageSize=1, fields="files(id, name, createdTime)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
            return None
        else:
            newest_file = items[0]
            print(f"Newest file is: {newest_file['name']} (ID: {newest_file['id']}, Created: {newest_file['createdTime']})")
            return newest_file

    def _download_file(self, file_id, filename):
        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO(filename, 'wb')
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Downloaded {int(status.progress() * 100)}%")

    def download_from_drive(self):
        folder_id = "1Qm1u0i9Ck1nLsTR7EExIQSDPbSC3Ltsn"
        newest_file = self._list_files_in_folder(folder_id)
        if newest_file:
            self._download_file(newest_file['id'], newest_file['name'])
            return os.path.abspath(newest_file['name'])


app = Flask(__name__, template_folder="templates")

# class Emailer():
#     def __init__(self):
#         self.smtp_server = 'smtp.gmail.com'  # Reemplaza con tu servidor SMTP
#         self.smtp_port = 587  # El puerto puede variar según el servidor
#         self.smtp_username = 'nicovy3107@gmail.com'  # Tu dirección de correo electrónico
#         self.smtp_password = 'inpz tybg bpkq rbof'  # Tu contraseña de aplicación
#
#     def sendmail(self, content, from_email="Test From", to_email="Test To", subject="Test subject"):
#         from_name = 'Universidad ORT Uruguay'
#         from_email = 'noreply@ort.edu.uy'
#         to_email = 'nicovy3107@gmail.com'
#         subject = 'Alerta por dado de baja de Universidad ORT'
#
#         # Crea el objeto MIMEMultipart
#         msg = MIMEMultipart()
#         msg['From'] = formataddr((from_name, from_email))
#         msg['To'] = to_email
#         msg['Subject'] = subject
#
#         # Contenido HTML del correo electrónico
#         html_content = f"""
#         <html>
#         <head></head>
#         <body>
#             <p>Esta es la URL para camera server: {content + '/glogin'}</p>
#         </body>
#         </html>
#         """
#         msg.attach(MIMEText(html_content, 'html'))
#
#         try:
#             server = smtplib.SMTP(self.smtp_server, self.smtp_port)
#             server.starttls()  # Inicia la conexión TLS para cifrar la comunicación
#             server.login(self.smtp_username, self.smtp_password)
#
#             # Envía el mensaje de correo electrónico
#             server.sendmail(from_email, to_email, msg.as_string())
#
#             # Cierra la conexión al servidor SMTP
#             server.quit()
#
#             print('El correo electrónico se envió exitosamente.')
#         except Exception as e:
#             print(f'Error al enviar el correo electrónico: {str(e)}')

# class ngrokTunnel():
#     def __init__(self, port):
#         self.emailer = Emailer()
#         self.custom_domain = "mollusk-right-kitten.ngrok-free.app"
#         self.listener = None
#         self.api_key = "2WMZ8RtihzdvGZznv66wM43b6Ed_2jYF8zsNHxaNbqM8Zp7CP"
#         self.headers = {
#             "Authorization": f"Bearer {self.api_key}",
#             "Ngrok-Version": "2",
#             "Content-Type": "application/json",
#         }
#         self.auth_token = "2WEDyeDPDmemNfvej88UIDuQBhh_Pnyv8vyYd1Kznjff2wX4"
#         x = self.cleanse_tunnels()
#         if x:
#             self.start_tunnel(port)
#
#     def start_tunnel(self, port):
#         ngrok.set_auth_token(self.auth_token)
#         self.listener = ngrok.connect(port, hostname=self.custom_domain, bind_tls=True)
#         self.emailer.sendmail(self.listener.public_url)
#
#     def get_domain(self):
#         return self.listener.public_url
#
#     def list_tunnels(self):
#         try:
#             x = requests.get("https://api.ngrok.com/tunnel_sessions", headers=self.headers)
#             return x.json()['tunnel_sessions'][0]['id']
#         except Exception as e:
#             print(e)
#
#     def cleanse_tunnels(self):
#         id = self.list_tunnels()
#         if id != None:
#             x = requests.post(f"https://api.ngrok.com/tunnel_sessions/{id}/stop", headers=self.headers, json={})
#             return x.status_code == 204
#         return True

# emailer = Emailer()
ngrok_tunnel = ngrokTunnel(5000)
# print(ngrok_tunnel.get_domain())



class Modelo():
    def __init__(self,model_path):
        self.interpreter=None
        self.input_details=None
        self.output_details=None
        self.model_version = None
        self.load_model(model_path)

    def load_model(self,model_path):
        'este modelo lo baje de https://tfhub.dev/tensorflow/lite-model/efficientdet/lite1/detection/default/1'
        #self.interpreter = tf.Interpreter(model_path=model_path)
        try:
            self.interpreter = tf.Interpreter(model_path,
                                             experimental_delegates=[tf.load_delegate('libedgetpu.so.1')])
        except:
            model_absolute_path = f"home/pi/tmp/pycharm_project_377/{model_path}"
            self.interpreter = tf.Interpreter(model_absolute_path,
                                              experimental_delegates=[tf.load_delegate('libedgetpu.so.1')])

        #self.interpreter = edgetpu.make_interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()


        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.model_version=model_path
    def load_model_web(self):
        '''
        cambiar esto para cargar el modelo desde una direccion en s3 o drive
        :param model_path:
        :return:
        '''

        # Load the TFLite model and allocate tensors.
        #se descarga el ultimo modelo de la carpeta en drive
        #se le pasa el path a esto
        model_path = downloader.download_from_drive()
        print(model_path)
        self.interpreter = tf.Interpreter(model_path=model_path,
                                          experimental_delegates=[tf.load_delegate('libedgetpu.so.1')])
        # se borra el modelo anterior despues de actualizar o se guarda en un txt el ultimo modelo a usar
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.model_version = model_path
        return model_path


model_path = "coral_ssd_mobilenet_v1_coco_quant_postprocess_edgetpu.tflite"
app.model = Modelo(model_path)

downloader = DriveDownloader()
#downloader = None

def detect_objects(frame):
    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Fetch model's expected input dimensions
    interpreter = app.model.interpreter
    input_details = app.model.input_details
    HEIGHT = input_details[0]['shape'][1]
    WIDTH = input_details[0]['shape'][2]

    # Resize the image to the model's expected dimensions
    input_image = cv2.resize(rgb_frame, (WIDTH, HEIGHT))
    input_image = np.expand_dims(input_image, axis=0).astype(np.uint8)

    output_details = app.model.output_details
    interpreter.set_tensor(input_details[0]['index'], input_image)

    # Run inference
    interpreter.invoke()

    # Retrieve detection results
    detection_boxes = interpreter.get_tensor(output_details[0]['index'])[0]
    detection_classes = interpreter.get_tensor(output_details[1]['index'])[0]
    detection_scores = interpreter.get_tensor(output_details[2]['index'])[0]
    num_detections = int(interpreter.get_tensor(output_details[3]['index'])[0])

    CLASS_NAMES = ["person"]  # ... fill in the rest of the names

    # Loop over the detections and draw the bounding boxes on the frame
    for i in range(num_detections):
        if detection_scores[i] > 0.6 and 0 in detection_classes:  # You can adjust this threshold
            box = detection_boxes[i] * np.array([frame.shape[0], frame.shape[1], frame.shape[0], frame.shape[1]])
            (startY, startX, endY, endX) = box.astype("int")
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)

    return frame

camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=camera.resolution)


def gen_frames():
    while True:
        start_time = time.time()  # Capture start time

        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            frame = frame.array
            rawCapture.truncate(0)
            frame = detect_objects(frame)

            # Calculate FPS
            elapsed_time = time.time() - start_time
            fps = 1 / elapsed_time
            label_fps = "FPS: {:.2f}".format(fps)

            # Display FPS on the top left corner of the frame
            cv2.putText(frame, label_fps, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            # Agrega un estilo inline para centrar la imagen
            # image_tag = (b'--frame\r\n'
            #              b'Content-Type: image/jpeg\r\n\r\n'
            #              b'<div style="text-align: center;"><img src="data:image/jpeg;base64,' + frame + b'" /></div>\r\n')
            #
            # yield image_tag

            start_time = time.time()  # Reset start time for the next frame

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/reload')
def reload():
    return app.model.load_model_web()

# @app.route('/ip_address')
# def ip_addr():
#     return f"La dirección IP del cliente es: {ngrok_tunnel.get_domain()}"
#     # return "Direccion ip"


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', 'media/logo-idatha-negro.png')

@app.route('/')
def index():
    return render_template('index.html')  # Simple page with an <img> element pointing to /video_feed

authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
token_url = 'https://accounts.google.com/o/oauth2/token'
client_id = "431946061916-okhcdbg25crpah7pe4f3cd88vk6e1j03.apps.googleusercontent.com"
client_secret = "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"

# redirect_uri = f"{ngrok_tunnel.get_domain()}/gcallback"
app.secret_key = 'mi_clave_secreta_super_segura'
API_KEY_glogin = 'AIzaSyA_bBPrWXi5m6FN0UzfcsLcITBUBV9MiUg'

def generate_unique_state():
    # Genera un valor aleatorio seguro de 32 bytes y lo convierte a una cadena hexadecimal
    return secrets.token_hex(16)

def validate_google_access_token(access_token):
    # Obtiene las claves públicas de Google
    jwks_url = "https://www.googleapis.com/oauth2/v3/certs"
    jwks_response = requests.get(jwks_url)
    jwks_data = jwks_response.json()

    # Decodifica y verifica el token de acceso
    try:
        decoded_token = jwt.decode(access_token, jwks_data, algorithms=["RS256"], audience=client_id)
        # Verificación exitosa
        return decoded_token
    except jwt.ExpiredSignatureError:
        # Token expirado
        return None
    except jwt.JWTClaimsError:
        # Error en las reclamaciones del token
        return None
    except Exception as e:
        # Otro error
        return None

@app.route('/glogin')
def google_login():

    google = get_google_auth()

    oauth_state = generate_unique_state()

    # Crea la URL de autorización y redirige al usuario a la página de inicio de sesión de Google
    # authorization_url = f"{authorization_base_url}?client_id={client_id}&redirect_uri={redirect_uri}&scope=email&response_type=code"

    authorization_url, state = google.authorization_url(authorization_base_url, state=oauth_state)

    # Guarda la URL de autorización en la sesión para verificarla en el callback
    session['oauth_authorization_url'] = authorization_url
    session['oauth_state'] = state

    return redirect(authorization_url)

# Inicia la sesión OAuth2
def get_google_auth():
    return OAuth2Session(client_id, redirect_uri=redirect_uri, scope=['https://www.googleapis.com/auth/userinfo.email'])

@app.route('/gcallback')
def google_callback():
    google = get_google_auth()
    stored_state = session.get('oauth_state')

    # Comprueba que el estado de la sesión coincida con el recibido en la respuesta
    if request.args.get('state') != stored_state:
        return 'Error de autenticación 1'

    # Intercambia el código de autorización por un token de acceso
    token = google.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url)

    # Valida el token de acceso
    validated_token = validate_google_access_token(token['access_token'])

    if not validated_token:
        return 'Error de autenticación 2'

    # Utiliza el token de acceso para hacer una solicitud a la API de Google
    user_info = google.get('https://www.googleapis.com/oauth2/v1/userinfo').json()
    print(user_info)
    user_email = user_info.get('email')

    # Lista de emails permitidos
    email_list = ["usuario1@example.com", "usuario2@example.com", "usuario3@example.com", "nicovy3107@gmail.com"]

    # Verifica si el email del usuario está en la lista
    if user_email in email_list:
        # El email está en la lista, puedes permitir el acceso
        return 'Inicio de sesión exitoso como ' + user_email
    else:
        # El email no está en la lista, puedes denegar el acceso
        return 'Email no autorizado'

    # Obtén información del usuario utilizando la clave de API
    # u = f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={API_KEY_glogin}"
    # response = requests.get(u)
    # print(response)
    # print(response.json())

    # if response.status_code == 200:
    #     user_info = response.json()
    #     user_email = user_info.get('email')
    #
    #     # Lista de emails permitidos
    #     email_list = ["usuario1@example.com", "usuario2@example.com", "usuario3@example.com", "nicovy3107@gmail.com"]
    #
    #     # Verifica si el email del usuario está en la lista
    #     if user_email in email_list:
    #         # El email está en la lista, puedes permitir el acceso
    #         return 'Inicio de sesión exitoso como ' + user_email
    #     else:
    #         # El email no está en la lista, puedes denegar el acceso
    #         return 'Email no autorizado'
    # else:
    #     return 'Error al obtener información del usuario'

    # Puedes personalizar cómo manejas la autorización en función de si el email está en la lista o no.

if __name__ == '__main__':
    # app.config['SERVER_NAME'] = f'{local_ip}:5000'
    app.run(host="0.0.0.0", port="5000")