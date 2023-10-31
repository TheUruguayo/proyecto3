from flask import Flask, render_template, Response, current_app
import cv2
import numpy as np
import tensorflow as tf

app = Flask(__name__)


camera = cv2.VideoCapture(0)  # Use 0 for default camera

# Load the TFLite model and allocate tensors.
# interpreter = tf.lite.Interpreter(model_path="D:\Dowloads\modelo_sin_coral.tflite")
# interpreter.allocate_tensors()
#
# input_details = interpreter.get_input_details()
# output_details = interpreter.get_output_details()

class Modelo():
    def __init__(self,model_path):
        self.interpreter=None
        self.input_details=None
        self.output_details=None
        self.model_version = None
        self.load_model(model_path)

    def load_model(self,model_path="D:\Dowloads\lite-model_efficientdet_lite1_detection_default_1.tflite"):
        'este modelo lo baje de https://tfhub.dev/tensorflow/lite-model/efficientdet/lite1/detection/default/1'
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
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
        model_path="D:\Dowloads\lite-model_efficientdet_lite2_detection_default_1.tflite"
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        # se borra el modelo anterior despues de actualizar o se guarda en un txt el ultimo modelo a usar
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.model_version = model_path
        return model_path

model_path = "D:\Dowloads\lite-model_efficientdet_lite1_detection_default_1.tflite"
app.model = Modelo(model_path)




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
        if detection_scores[i] > 0.5:  # You can adjust this threshold
            box = detection_boxes[i] * np.array([frame.shape[0], frame.shape[1], frame.shape[0], frame.shape[1]])
            (startY, startX, endY, endX) = box.astype("int")
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)

            # Add the model version as label text
            cv2.putText(frame, app.model.model_version, (startX, startY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    return frame


def gen_frames():
    while True:
        success, frame = camera.read()

        # Use the TFLite model to detect objects on the frame
        frame = detect_objects(frame)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


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
