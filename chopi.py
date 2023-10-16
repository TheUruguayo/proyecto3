import pickle
import os.path
import time

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import io
from googleapiclient.http import MediaIoBaseDownload
from flask import Flask, redirect, session, request, render_template, Response, current_app
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


app = Flask(__name__)

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
print(ngrok_tunnel.get_domain())



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

            start_time = time.time()  # Reset start time for the next frame


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/reload')
def reload():
    return app.model.load_model_web()

@app.route('/ip_address')
def ip_addr():
    return f"La dirección IP del cliente es: {ngrok_tunnel.get_domain()}"
    # return "Direccion ip"



@app.route('/')
def index():
    return render_template('index.html')  # Simple page with an <img> element pointing to /video_feed

authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
token_url = 'https://accounts.google.com/o/oauth2/token'
client_id = "431946061916-okhcdbg25crpah7pe4f3cd88vk6e1j03.apps.googleusercontent.com"
client_secret = "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"

redirect_uri = f"{ngrok_tunnel.get_domain()}/gcallback"
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
    app.run(host="0.0.0.0", port="5000")

# ------------------------------------------------

import json, os, sqlite3, requests
from oauthlib.oauth2 import WebApplicationClient

from flask import Flask, redirect, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from db import init_db_command
from user import User
from ngrok import ngrokTunnel

# Configuration
GOOGLE_CLIENT_ID = "431946061916-okhcdbg25crpah7pe4f3cd88vk6e1j03.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Flask app setup
app = Flask(__name__)
app.secret_key = os.urandom(24)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# ngrok_tunnel = ngrokTunnel(5000)

@login_manager.unauthorized_handler
def unauthorized():
    return "You must be logged in to access this content.", 403

# Naive database setup
try:
    init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass

# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route("/")
def index():
    if current_user.is_authenticated:
        return (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<img src="{}" alt="Google profile pic"></img></div>'
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name, current_user.email, current_user.profile_pic
            )
        )
    else:
        return '<a class="button" href="/login">Google Login</a>'


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    # request_uri = client.prepare_request_uri(
    #     authorization_endpoint,
    #     redirect_uri="mollusk-right-kitten.ngrok-free.app" + "/gcallback",
    #     scope=["openid", "email", "profile"],
    # )
    return redirect(request_uri)


@app.route("/gcallback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in our db with the information provided
    # by Google
    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    # Doesn't exist? Add to database
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


from OpenSSL import SSL
context = SSL.Context(SSL.TLSv1_2_METHOD)
context.use_privatekey_file("../../certs3/server.key")
context.use_certificate_file("../../certs3/server.crt")


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5000, ssl_context="adhoc")
    app.run(host='127.0.0.1', ssl_context=context)

# import os
#
# from flask import Flask, redirect, session, request, render_template, Response
# from flask_talisman import Talisman
# from pyngrok import ngrok
# from requests_oauthlib import OAuth2Session
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.utils import formataddr
# import requests, smtplib, secrets, jwt
#
# # --------------------------------------------------------------------------------------
# app = Flask(__name__)
#
# # Configura Flask para que use HTTPS (SSL)
# app.config['SESSION_COOKIE_SECURE'] = True
# app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # O 'Strict' según tus necesidades
# app.config['SESSION_COOKIE_HTTPONLY'] = True
# app.config['SESSION_COOKIE_SECURE'] = True
# app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # O 'Strict' según tus necesidades
# app.config['SESSION_COOKIE_HTTPONLY'] = True
# app.config['SESSION_COOKIE_SECURE'] = True
# app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # O 'Strict' según tus necesidades
# app.config['SESSION_COOKIE_HTTPONLY'] = True
# app.config['SESSION_COOKIE_SECURE'] = True
# app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # O 'Strict' según tus necesidades
# app.config['SESSION_COOKIE_HTTPONLY'] = True
# app.secret_key = 'mi_clave_secreta_super_segura'
#
# # Configura Flask-Talisman
# # csp = {
# #     'default-src': "'self'",
# #     'img-src': '*',
# #     'style-src': ["'self'", 'maxcdn.bootstrapcdn.com'],
# #     'strict-transport-security': 'max-age=31536000; includeSubDomains; preload'  # Configura HSTS
# # }
# # talisman = Talisman(
# #     app,
# #     content_security_policy=csp,
# #     force_https=True,  # Redirecciona todas las solicitudes HTTP a HTTPS
# # )
# # --------------------------------------------------------------------------------------
# # Parámetros Google Login
# authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
# token_url = 'https://accounts.google.com/o/oauth2/token'
# client_id = "431946061916-okhcdbg25crpah7pe4f3cd88vk6e1j03.apps.googleusercontent.com"
# client_secret = "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"
# google_api_key = 'AIzaSyA_bBPrWXi5m6FN0UzfcsLcITBUBV9MiUg'
# redirect_uri = "https://mollusk-right-kitten.ngrok-free.app/gcallback"
# # --------------------------------------------------------------------------------------
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
#         subject = 'NGROK'
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
#             <p>Esta es la URL para camera server: {content}</p>
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
#
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
#         # self.listener = ngrok.connect(port, hostname=self.custom_domain, bind_tls=True)
#         cf = '../../certs/certificate.pem'
#         kf = '../../certs/private-key.pem'
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
#
# ngrok_tunnel = ngrokTunnel(5000)
# print(ngrok_tunnel.get_domain())
# # --------------------------------------------------------------------------------------
#
# # Rutas de tu aplicación Flask
# @app.route('/')
# def home():
#     return '¡Hola, mundo!'

# # Configura la sesión OAuth2
# oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=['email'])
# @app.route('/login')
# def login():
#     authorization_url, state = oauth.authorization_url(
#         'https://accounts.google.com/o/oauth2/auth',
#         # El scope puede ser personalizado según tus necesidades
#     )
#     session['oauth_state'] = state
#     return redirect(authorization_url)
#
# @app.route('/gcallback')
# def callback():
#     token = oauth.fetch_token(
#         'https://accounts.google.com/o/oauth2/token',
#         authorization_response=request.url,
#         client_secret=client_secret
#     )
#
#     # Ahora puedes utilizar el token para hacer solicitudes a la API de Google
#     response = oauth.get('https://www.googleapis.com/oauth2/v1/userinfo')
#     user_info = response.json()
#     user_email = user_info.get('email')

# def generate_unique_state():
#     # Genera un valor aleatorio seguro de 32 bytes y lo convierte a una cadena hexadecimal
#     return secrets.token_hex(16)
#
#
# def validate_google_access_token(access_token, jwks_url= "https://www.googleapis.com/oauth2/v3/certs", client_id = client_id):
#     try:
#         # Obtiene las claves públicas de Google
#         jwks_response = requests.get(jwks_url)
#         jwks_data = jwks_response.json()
#
#         # Decodifica el token de acceso
#         decoded_token = jwt.decode(
#             access_token,
#             jwks_data,  # Debes extraer las claves públicas adecuadas de jwks_data
#             algorithms=["RS256"],
#             audience=client_id
#         )
#
#         # Verificación exitosa
#         return decoded_token
#     except jwt.ExpiredSignatureError:
#         # Token expirado
#         return None
#     except jwt.JWTClaimsError:
#         # Error en las reclamaciones del token
#         return None
#     except Exception as e:
#         # Maneja otros errores adecuadamente (puedes imprimir o registrar estos errores para depuración)
#         print(f"Error en la validación del token: {str(e)}")
#         return None

# def validate_google_access_token(access_token):
#     # Obtiene las claves públicas de Google
#     jwks_url = "https://www.googleapis.com/oauth2/v3/certs"
#     jwks_response = requests.get(jwks_url)
#     jwks_data = jwks_response.json()
#
#     # Decodifica y verifica el token de acceso
#     try:
#         decoded_token = jwt.decode(access_token, jwks_data, algorithms=["RS256"], audience=client_id)
#         # Verificación exitosa
#         return decoded_token
#     except jwt.ExpiredSignatureError:
#         # Token expirado
#         return None
#     except jwt.JWTClaimsError:
#         # Error en las reclamaciones del token
#         return None
#     except Exception as e:
#         # Otro error
#         return None

# @app.route('/glogin')
# def google_login():
#     google = get_google_auth()
#
#     oauth_state = generate_unique_state()
#
#     # Crea la URL de autorización y redirige al usuario a la página de inicio de sesión de Google
#     # authorization_url = f"{authorization_base_url}?client_id={client_id}&redirect_uri={redirect_uri}&scope=email&response_type=code"
#     # redirect_uri = f"{ngrok_tunnel.get_domain()}/gcallback"
#
#     authorization_url, state = google.authorization_url(authorization_base_url, state=oauth_state)
#
#     # Guarda la URL de autorización en la sesión para verificarla en el callback
#     session['oauth_authorization_url'] = authorization_url
#     session['oauth_state'] = state
#
#     return redirect(authorization_url)
#
# # Inicia la sesión OAuth2
# def get_google_auth():
#     redirect_uri = f"{ngrok_tunnel.get_domain()}/gcallback"
#     return OAuth2Session(client_id, redirect_uri=redirect_uri, scope=['https://www.googleapis.com/auth/userinfo.email'])
#
# @app.route('/gcallback')
# def google_callback():
#     google = get_google_auth()
#     stored_state = session.get('oauth_state')
#
#     # Comprueba que el estado de la sesión coincida con el recibido en la respuesta
#     if request.args.get('state') != stored_state:
#         return 'Error de autenticación 1'
#
#     # Intercambia el código de autorización por un token de acceso
#     # token = google.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url)
#
#     # Valida el token de acceso
#     # validated_token = validate_google_access_token(token['access_token'])
#
#     # if not validated_token:
#     #     return 'Error de autenticación 2'
#
#     # Utiliza el token de acceso para hacer una solicitud a la API de Google
#     user_info = google.get('https://www.googleapis.com/oauth2/v1/userinfo')
#     print(user_info)
#     user_info = user_info.json()
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

# if __name__ == '__main__':
#
#     app.run(host="0.0.0.0", port="5000", ssl_context=("../../certs2/certificate.pem", "../../certs2/decrypted-private-key.pem"))
