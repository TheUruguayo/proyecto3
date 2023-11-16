import glob

import cv2
from flask import Flask, redirect, session, request, render_template, Response, send_from_directory, flash, url_for, \
    jsonify, make_response, send_file
from functools import wraps
import subprocess, re, os, bcrypt
from dotenv import load_dotenv, find_dotenv
from flask_cors import CORS
# ------------- IMPORT MODULES ----------------------
from modules.model import Modelo, gen_frames, reload_camera
from modules.ngrok import ngrokTunnel
from modules.db import UsersDB, RecordingsDB
from modules.emailer import Emailer
# ---------------------------------------------------

load_dotenv(find_dotenv())

app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path='/static')
app.secret_key = os.getenv("APP-SECRET_KEY")
app_port = int(os.getenv("APP-PORT"))
cors = CORS(app, resources={r"/static/recordings/*": {"origins": "*"}})


ngrok_tunnel = ngrokTunnel(app_port)
emailer = Emailer()

folder_id = os.getenv("DRIVE-FOLDER_ID")
model_path = os.getenv("DRIVE-MODEL_PATH")
print("Modelo a cargar", model_path)
app.model = Modelo(model_path, folder_id)

users_db = UsersDB(os.path.join(os.path.dirname(__file__), 'database/users.db'))
recordings_db = RecordingsDB(os.path.join(os.path.dirname(__file__), 'database/recordings.db'))
# recordings_db.create_table()
# users_db.create_table()
# recordings_db.recreate_database()
# users_db.add_user(os.getenv("EMAILER-USERNAME"), '123456')


user_logged_in = ""



@app.route('/users/add', methods=['POST'])
def registro():
    user_data = request.get_json()
    username = user_data.get("username")
    password = user_data.get("password")

    if not username or not password:
        return jsonify({"error": "Faltan datos de usuario o contraseña"}), 400
    status = users_db.add_user(username, password) # True correcto y False error
    if status:
        content = {
            "url": "https://mollusk_right_kitten.ngrok-free.app", # ngrokTunnel.get_domain(),
            "password": password
        }
        emailer.sendmail(content, subject="add_user", to_email=username)
        return jsonify({"message": "El usuario se ha agregado correctamente!", "color": "green"}), 201
    else:
        return jsonify({"message": "El usuario ya está registrado!", "color": "red"}), 201

@app.route('/users/list', methods=['GET'])
def obtener_usuarios():
    users = users_db.get_users()
    return jsonify(users)

@app.route('/users/delete', methods=['DELETE'])
def borrar_usuario():
    global user_logged_in
    data = request.get_json()
    username = data.get("username")
    if username != user_logged_in:
        deleted = users_db.delete_user(username)
        msg = "Usuario borrado correctamente" if deleted else "El usuario no existe en la base de datos"
        color = "green" if deleted else "red"
    else:
        msg = "No puedes eliminar el usuario con el que iniciaste sesión!"
        color = "red"
    return jsonify({"message": msg, "color": color}), 200

@app.route('/recordings/list', methods=['GET'])
def obtener_recordings():
    rec = recordings_db.get_recordings_ordered_by_date()
    return jsonify(rec)

@app.route("/recordings/delete/<path:video_path>")
def delete_recording(video_path):
    try:
        rec = recordings_db.get_recording_by_videoPath(video_path)
        recordings_db.delete_recording(rec["name"])
        print(f"Recording de {video_path} eliminado correctamente")
        return True, 200
    except Exception as e:
        print(e)
        return False, 4040
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(app, recordings_db),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', 'media/logo-idatha-negro.png')

@app.route('/thumbnails/<path:thumbnail_filename>')
def serve_thumbnail(thumbnail_filename): #path relativo
    return send_file(thumbnail_filename)

@app.route('/play_video/<path:video_filename>')
def play_video(video_filename):
    return send_file(video_filename, as_attachment=True, mimetype='video/mp4')

@app.route('/delete_video/<path:video_filename>', methods=['DELETE'])
def delete_video(video_filename):
    try:
        print("DELETE", video_filename)
        video_filename = '/' + video_filename
        rec = recordings_db.get_recording_by_videoPath(video_filename)
        if rec:
            os.remove(rec['video_path'])
            os.remove(rec['thumbnail_path'])
            recordings_db.delete_recording(rec['name'])
            return jsonify(success=True, message='Grabación eliminada exitosamente')
        else:
            return jsonify(success=False, message='La grabación no existe en la base de datos')
    except Exception as e:
        return jsonify(success=False, message=str(e))

@app.route('/')
def index():
    global user_logged_in
    if not session.get('logged_in') or user_logged_in == "":
        session['logged_in'] = False
        flash('Please log in first.', 'info')
        return redirect(url_for('login'))
    reload_camera()
    return render_template('index.html',
                           model_text=os.getenv("DRIVE-MODEL_PATH"),
                           clave_secreta=os.getenv("APP-SECRET_KEY"),
                           username=user_logged_in,
                           contrasenaSecreta=os.getenv("DATABASE-SECRET_PASSWORD") )

@app.route('/login', methods=['GET', 'POST'])
def login():
    global user_logged_in
    if session.get('logged_in') is False or user_logged_in == "":
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            user_data = users_db.get_user_by_username(username)
            if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['password']):
                session['logged_in'] = True
                user_logged_in = username
                if password == os.getenv("DATABASE-SECRET_PASSWORD"):
                    return redirect(url_for('func_change_password'))
                flash('You were successfully logged in!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Login failed!', 'danger')
        return render_template('login.html')
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    global user_logged_in
    session['logged_in'] = False
    user_logged_in = ""
    flash('You were logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/reload_model')
# @protect_endpoint
def reload():
    # return app.model.load_model_web()
    model_path, model_name = app.model.load_model_web()
    response = {'modelPath': model_path, 'modelName': model_name}

    # ######### Guarda en el código pero no persiste #####################
    os.environ["DRIVE-MODEL_PATH"] = model_name
    # ########## Guardar de manera persistente en variable de entorno ####
    env_file_path = find_dotenv()
    with open(env_file_path, "r") as env_file:
        lines = env_file.readlines()

    for i, line in enumerate(lines):
        if line.startswith("DRIVE-MODEL_PATH="):
            lines[i] = f"DRIVE-MODEL_PATH={model_name}\n"
            print(lines[i])

    with open(env_file_path, "w") as env_file:
        env_file.writelines(lines)
    ######################################################################
    print("Se carga el modelo", os.getenv("DRIVE-MODEL_PATH"))
    return jsonify(response)

@app.route('/users/change_password', methods=['GET', 'POST'])
def func_change_password():
    global user_logged_in
    if not session.get('logged_in') or user_logged_in == "":
        flash('Please log in first.', 'info')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Lógica para cambiar la contraseña aquí
        current_password = request.form['current_password']
        new_password1 = request.form['new_password1']
        new_password2 = request.form['new_password2']

        # Realiza la verificación de la contraseña actual y el cambio de contraseña
        user_data = users_db.get_user_by_username(user_logged_in)
        if user_data and bcrypt.checkpw(current_password.encode('utf-8'), user_data['password']):
            if new_password1 == new_password2:
                print("Contraseñas coinciden!")
                # Actualiza la contraseña en la base de datos
                new_hashed_password = bcrypt.hashpw(new_password1.encode('utf-8'), bcrypt.gensalt())
                print(new_hashed_password)
                # Aquí deberías actualizar la contraseña en la base de datos
                status = users_db.update_password(user_logged_in, new_hashed_password)
                print(status)
                flash('Password changed successfully!', 'success')
                return redirect(url_for("index"))
            else:
                flash('New passwords do not match.', 'danger')
        else:
            flash('Incorrect current password.', 'danger')

    return render_template('change_password.html', username=user_logged_in)

@app.route('/model/change_folder', methods=['POST'])
def change_model_folder():
    try:
        folder_id = request.form["folder_id"]
        print("Este es el nuevo folder id", folder_id)
        # ######### Guarda en el código pero no persiste #####################
        os.environ["DRIVE-FOLDER_ID"] = folder_id
        # ########## Guardar de manera persistente en variable de entorno ####
        env_file_path = find_dotenv()
        with open(env_file_path, "r") as env_file:
            lines = env_file.readlines()

        for i, line in enumerate(lines):
            if line.startswith("DRIVE-FOLDER_ID="):
                lines[i] = f"DRIVE-FOLDER_ID={folder_id}\n"
                print(lines[i])

        with open(env_file_path, "w") as env_file:
            env_file.writelines(lines)
        ######################################################################
        response = {"message": "Carpeta de modelos cambiada exitosamente", "success": True}
    except Exception as e:
        response = {"message": str(e), "success": False}
    return jsonify(response)


if __name__ == '__main__':
    # app.config['SERVER_NAME'] = f'{local_ip}:5000'
    app.run(host="0.0.0.0", port=app_port)

    # GUARDADO DE VIDEOS