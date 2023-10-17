from flask import Flask, redirect, session, request, render_template, Response, current_app, send_from_directory, flash, url_for
import atexit
# ------------- IMPORT MODULES ----------------------
from ngrok import ngrokTunnel
from model import Modelo, gen_frames, camera, reload_camera
# ---------------------------------------------------

app = Flask(__name__, template_folder="templates")
app.secret_key = 'mi_clave_secreta_super_segura'

ngrok_tunnel = ngrokTunnel(5000)

folder_id = "" # Carpeta en drive donde buscará modelos
model_path = "coral_ssd_mobilenet_v1_coco_quant_postprocess_edgetpu.tflite"
app.model = Modelo(model_path, folder_id)

users = {
    "nicovy3107@gmail.com": "1234"
}  # You can expand this dictionary or use a database

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['logged_in'] = True
            flash('You were successfully logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed!', 'danger')
    return render_template('login.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(app),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', 'media/logo-idatha-negro.png')

@app.route('/')
def index():
    if not session.get('logged_in'):
        flash('Please log in first.', 'info')
        return redirect(url_for('login'))
    reload_camera()
    return render_template('index.html')

@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('You were logged out.', 'info')
    return redirect(url_for('login'))

import time
@app.route('/reload_model')
def reload():
    return app.model.load_model_web()


if __name__ == '__main__':
    # app.config['SERVER_NAME'] = f'{local_ip}:5000'
    app.run(host="0.0.0.0", port="5000")


    # DEFINIR ENVIRONMENT PARA CLAVES / CONTRASEÑAS /ETC
    # MANEJO DE LOGIN / USUARIOS / ROLES ? / ETC
    # GUARDADO DE VIDEOS