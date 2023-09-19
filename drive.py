import pickle
import os.path
import time

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import io
from googleapiclient.http import MediaIoBaseDownload
from flask import Flask, render_template, Response, current_app
import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera

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

API_KEY = 'AIzaSyD4E-EnfS8h0AlNlvKWzgBsRYqm0Sx32Mw'

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

@app.route('/')
def index():
    return render_template('index.html')  # Simple page with an <img> element pointing to /video_feed


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")

