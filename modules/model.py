# CLASE MODELO Y MANEJO DE CAMARA RASPI

import tflite_runtime.interpreter as tf
from modules.DriveDownloader import DriveDownloader
import cv2, time, os
import numpy as np
from flask import jsonify
from picamera.array import PiRGBArray
from picamera import PiCamera

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
        # 'este modelo lo baje de https://tfhub.dev/tensorflow/lite-model/efficientdet/lite1/detection/default/1'
        # self.interpreter = tf.Interpreter(model_path=model_path)
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
        '''
        cambiar esto para cargar el modelo desde una direccion en s3 o drive
        :param model_path:
        :return:
        '''

        # Load the TFLite model and allocate tensors.
        #se descarga el ultimo modelo de la carpeta en drive
        #se le pasa el path a esto
        # model_path = self.downloader.download_from_drive()
        # print(f"El path absoluto al modelo descargado es: {model_path}")

        model_folder = "models"  # Ruta de la carpeta donde se almacenan los modelos

        # Verificar si el último modelo ya está en la carpeta "models"
        folder_path = os.path.join(model_folder, self.model_version)

        model_path = self.downloader.download_from_drive(folder_path)
        print(f"El path absoluto al modelo descargado es: {model_path}")

        # if not os.path.exists(folder_path):
        #     # Si no existe, descarga el modelo utilizando download_from_drive
        #     model_path = self.downloader.download_from_drive(folder_path)
        #         #     print(f"El path absoluto al modelo descargado es: {model_path}")
        # else:
        #     # Si el modelo ya existe, eliminarlo y luego descargar el nuevo modelo
        #     # os.remove(folder_path)
        #     model_path = self.downloader.download_from_drive(folder_path)
        #     print(f"El path absoluto al modelo descargado es: {model_path}")

        # model_path = os.path.abspath(model_path)
        self.interpreter = tf.Interpreter(model_path=model_path,
                                          experimental_delegates=[tf.load_delegate('libedgetpu.so.1')])
        # se borra el modelo anterior despues de actualizar o se guarda en un txt el ultimo modelo a usar
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.model_version = model_path
        # response = {'modelPath': model_path, 'modelName': os.path.basename(model_path)}
        return model_path, os.path.basename(model_path)


def detect_objects(frame, app):
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

def gen_frames(app):
    global rawCapture
    while True:
        start_time = time.time()  # Capture start time

        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            frame = frame.array
            rawCapture.truncate(0)
            frame = detect_objects(frame, app)

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

def reload_camera():
    global camera
    if camera:
        camera.close()
        while camera._encoders:
            # Espera hasta que la cámara haya liberado completamente el buffer
            time.sleep(1)
    # time.sleep(0.1)
    camera = init_camera()

def init_camera():
    # global rawCapture
    camera = PiCamera()
    camera.resolution = (320, 240)
    camera.framerate = 30
    return camera

camera = init_camera()
rawCapture = PiRGBArray(camera, size=camera.resolution)
