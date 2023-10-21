from flask import Flask, redirect, session, request, render_template, Response, send_from_directory, flash, url_for, jsonify, make_response
from functools import wraps
import subprocess, re, os, bcrypt
from dotenv import load_dotenv, find_dotenv
# ------------- IMPORT MODULES ----------------------
from modules.model import Modelo, gen_frames, reload_camera
from modules.ngrok import ngrokTunnel
from modules.db import UsersDB
from modules.emailer import Emailer
# ---------------------------------------------------

load_dotenv(find_dotenv())

app = Flask(__name__, template_folder="templates")
app.secret_key = os.getenv("APP-SECRET_KEY")
app_port = int(os.getenv("APP-PORT"))

# ngrok_tunnel = ngrokTunnel(app_port)
emailer = Emailer()

folder_id = os.getenv("DRIVE-FOLDER_ID")
model_path = os.getenv("DRIVE-MODEL_PATH")
print("Modelo a cargar", model_path)
app.model = Modelo(model_path, folder_id)

users_db = UsersDB(os.path.join(os.path.dirname(__file__), 'database/users.db'))
users_db.create_table()
# users_db.recreate_database()
users_db.add_user(os.getenv("EMAILER-USERNAME"), '123456')
print(users_db.get_users())
user_logged_in = ""

# pwd = os.getenv("DATABASE-SECRET_PASSWORD")
# salt =

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
#

# def no_es_fuente_confiable():
#     custom_header = request.headers.get('X-App-Header')
#     print(f"Custom header: {custom_header}")
#     if custom_header == app.secret_key:
#         return False
#     else:
#         return True
# def protect_endpoint(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         # Verifica si la solicitud proviene de una fuente confiable, como la propia aplicación
#         if no_es_fuente_confiable():
#             return redirect(url_for('index'))
#         return f(*args, **kwargs)
#     return decorated_function
@app.route('/users/list', methods=['GET'])
# @protect_endpoint
def obtener_usuarios():
    users = users_db.get_users()
    return jsonify(users)

@app.route('/users/delete', methods=['DELETE'])
# @protect_endpoint
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

@app.route('/video_feed')
# @protect_endpoint
def video_feed():
    return Response(gen_frames(app),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/static/<path:filename>')
# @protect_endpoint
def serve_static(filename):
    return send_from_directory('static', 'media/logo-idatha-negro.png')

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
            # if username in users and users[username] == password:
            #     session['logged_in'] = True
            #     flash('You were successfully logged in!', 'success')
            #     return redirect(url_for('index'))
            # else:
            #     flash('Login failed!', 'danger')
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

# @app.route('/ip_address')
# def ip_address():
#     ip_address = get_ip_address("wlan0")  # Cambia a "eth0" si es necesario
#     if ip_address:
#         return f"La dirección IP de la interfaz wlan0 es: {ip_address}"
#     else:
#         return "No se pudo obtener la dirección IP."
#     # return f"La dirección IP es {request.remote_addr} - {request.remote_user} o {ngrok_tunnel.get_domain()}"
#
# def get_ip_address(interface):
#     try:
#         # Ejecuta el comando ifconfig y captura su salida
#         result = subprocess.check_output(["ifconfig", interface]).decode()
#
#         # Utiliza una expresión regular para buscar la dirección IP en la salida
#         ip_match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', result)
#
#         if ip_match:
#             ip_address = ip_match.group(1)
#             return ip_address
#
#         return None
#     except Exception as e:
#         # Maneja cualquier error que pueda ocurrir
#         print("Error al obtener la dirección IP:", str(e))
#         return None

if __name__ == '__main__':
    # app.config['SERVER_NAME'] = f'{local_ip}:5000'
    app.run(host="0.0.0.0", port=app_port)

    # LOGIN DE USUARIOS
    """
    - funciona crear usuarios y verificarlo en la pantalla de login
    * Pronto boton de manejar usuarios
        * Agregar boton para cambiar contraseña
        * desplegar la lista de usuarios correctamente
        * sacar combo box de roles
        * agregar usuario manda mail con contraseña default
        * contraseña default debería de tener un patron reconocible para cambiar la contraseña instantáneamente
    """

    # GUARDADO DE VIDEOS

    # BOTON QUE RECIBA URL DE DRIVE PARA DESCARGAR MODELOS (MODIFICAR URL DE DESCARGA)