from flask import Flask, render_template, Response
import cv2
import numpy as np
import tensorflow as tf

app = Flask(__name__)

camera = cv2.VideoCapture(0)  # Use 0 for default camera

# Load the TFLite model and allocate tensors.
interpreter = tf.lite.Interpreter(model_path="coral_ssd_mobilenet_v1_coco_quant_postprocess_edgetpu.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
class Modelo():
    def __init__(self):
        self.interpreter=None
        self.input_details=None
        self.output_details=None

    def load_model(self,model_path="coral_ssd_mobilenet_v1_coco_quant_postprocess_edgetpu.tflite"):
        # Load the TFLite model and allocate tensors.
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

def detect_objects(frame):
    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Resize and normalize the image
    input_image = cv2.resize(rgb_frame, (384, 384))
    input_image = np.expand_dims(input_image, axis=0).astype(np.uint8)

    # Set the tensor to point to the input data to be used for inference
    interpreter.set_tensor(input_details[0]['index'], input_image)

    # Run inference
    interpreter.invoke()

    # Retrieve detection results
    detection_boxes = interpreter.get_tensor(output_details[0]['index'])[0]
    detection_classes = interpreter.get_tensor(output_details[1]['index'])[0]
    detection_scores = interpreter.get_tensor(output_details[2]['index'])[0]
    num_detections = int(interpreter.get_tensor(output_details[3]['index'])[0])

    # Loop over the detections and draw the bounding boxes on the frame
    for i in range(num_detections):
        if detection_scores[i] > 0.5:  # You can adjust this threshold
            box = detection_boxes[i] * np.array([frame.shape[0], frame.shape[1], frame.shape[0], frame.shape[1]])
            (startY, startX, endY, endX) = box.astype("int")
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)

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


@app.route('/')
def index():
    return render_template('index.html')  # Simple page with an <img> element pointing to /video_feed


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")
