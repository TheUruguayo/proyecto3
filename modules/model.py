# CLASE MODELO Y MANEJO DE CAMARA RASPI

import tflite_runtime.interpreter as tf
from modules.DriveDownloader import DriveDownloader
from modules.db import RecordingsDB
import cv2, time, os, json
from datetime import datetime
import numpy as np
from flask import jsonify
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL import Image

class Modelo():
    def __init__(self, model_path, app):
        self.interpreter=None
        self.input_details=None
        self.output_details=None
        self.model_version = None
        self.downloader = DriveDownloader()
        self.app = app
        self.load_model(model_path)

    def load_model(self,model_path):
        try:
            self.interpreter = tf.Interpreter(f"models/{model_path}",
                                             experimental_delegates=[tf.load_delegate('libedgetpu.so.1')])
        except:
            model_absolute_path = f"home/pi/tmp/pycharm_project_377/models/{model_path}"
            self.interpreter = tf.Interpreter(model_absolute_path,
                                              experimental_delegates=[tf.load_delegate('libedgetpu.so.1')])

        #self.interpreter = edgetpu.make_interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()


        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.model_version=model_path

    def load_model_web(self):

        model_folder = "models"  # Ruta de la carpeta donde se almacenan los modelos

        # Verificar si el último modelo ya está en la carpeta "models"
        folder_path = os.path.abspath(os.path.join(model_folder, self.model_version))

        model_path = self.downloader.download_from_drive(folder_path)
        print(f"El path absoluto al modelo descargado es: {model_path}")

        self.interpreter = tf.Interpreter(model_path=model_path,
                                          experimental_delegates=[tf.load_delegate('libedgetpu.so.1')])
        # se borra el modelo anterior despues de actualizar o se guarda en un txt el ultimo modelo a usar
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.model_version = model_path
        return model_path, os.path.basename(model_path)


def detect_objects(frame, app):
    retorno = False # ¨Para indicar si hubo detección o no

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
            retorno = True

    return frame, retorno

# def gen_frames(app):
#     global rawCapture
#     while True:
#         start_time = time.time()  # Capture start time
#
#         for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
#             frame = frame.array
#             rawCapture.truncate(0)
#             frame = detect_objects(frame, app)
#
#             # Calculate FPS
#             elapsed_time = time.time() - start_time
#             fps = 1 / elapsed_time
#             label_fps = "FPS: {:.2f}".format(fps)
#
#             # Display FPS on the top left corner of the frame
#             cv2.putText(frame, label_fps, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
#
#             ret, buffer = cv2.imencode('.jpg', frame)
#             frame = buffer.tobytes()
#
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#
#             start_time = time.time()  # Reset start time for the next frame

def gen_frames(app, db):
    global rawCapture
    recording = False
    start_time = 0
    recording_duration = 15
    pre_event_duration = 2
    frame_buffer = []

    while True:
        s_time = time.time()
        frames_for_video = []

        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            frame = frame.array
            rawCapture.truncate(0)
            frame, ret = detect_objects(frame, app)

            if ret:
                if not recording:
                    print("Comienza la grabación")
                    recording = True
                    start_time = time.time()
                    frames_for_video = []

            elapsed_time = time.time() - start_time
            # print(elapsed_time)

            if elapsed_time >= recording_duration:
                recording = False
                save_video(frames_for_video, db)
                frames_for_video = []

            # Calculate FPS
            e_time = time.time() - s_time
            fps = 1 / e_time
            label_fps = "FPS: {:.2f}".format(fps)

            # Display FPS on the top left corner of the frame
            cv2.putText(frame, label_fps, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            if recording:
                frame_buffer.append(frame)
                frames_for_video.append(frame)

            while frame_buffer and (time.time() - start_time - pre_event_duration > 0):
                frame_buffer.pop(0)

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            s_time = time.time()  # Reset start time for the next frame

def save_video(frames, db):
    if len(frames) > 0:
        print("Comienzo a guardar video")
        current_time = datetime.now()
        video_name = current_time.strftime("%d-%m-%y %H-%M")

        video_path = f"static/recordings/{video_name}.mp4"
        thumbnail_path = f"static/thumbnail/{video_name}.jpg"

        # Guarda el video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_path, fourcc, 30.0, (640, 480))
        for frame in frames:
            image = cv2.imdecode(np.frombuffer(frame, np.uint8), -1)
            out.write(image)
        out.release()

        # Guarda la miniatura
        # first_frame = cv2.imdecode(np.frombuffer(frames[0], np.uint8), -1)
        # if first_frame is not None:
        #     thumbnail_image = Image.fromarray(cv2.cvtColor(first_frame, cv2.COLOR_BGR2RGB))
        #     thumbnail_image.save(thumbnail_path)
        # else:
        #     print("El primer frame no es válido. No se pudo generar la miniatura.")

        # Agrega el registro al historial de grabaciones
        recording_entry = {
            "name": video_name,
            "video_path": video_path,
            "thumbnail_path": thumbnail_path,
            "created_at": current_time.strftime("%Y-%m-%d %H:%M:%S")
        }

        db.add_recording(
            recording_entry["name"],
            recording_entry["video_path"],
            recording_entry["thumbnail_path"],
            recording_entry["created_at"]
        )
# def replay_video(video_path):
#     try:
#         # Abre el archivo de video
#         cap = cv2.VideoCapture(video_path)
#
#         if not cap.isOpened():
#             return "No se pudo abrir el archivo de video.", 404
#         return cap
#     except:
#         return None
#
# def generate_frames(cap):
#     while True:
#         success, frame = cap.read()
#         if not success:
#             break
#
#         ret, buffer = cv2.imencode('.jpg', frame)
#         if not ret:
#             break
#
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

def reload_camera():
    global camera
    if camera:
        camera.close()
        while camera._encoders:
            time.sleep(1) # Espera hasta que la cámara haya liberado completamente el buffer
    camera = init_camera()

def close_camera():
    global camera
    if camera:
        camera.close()
        while camera._encoders:
            time.sleep(1) # Espera hasta que la cámara haya liberado completamente el buffer

def init_camera():
    # global rawCapture
    camera = PiCamera()
    camera.resolution = (320, 240)
    camera.framerate = 30
    return camera

camera = init_camera()
rawCapture = PiRGBArray(camera, size=camera.resolution)
