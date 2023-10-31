import sqlite3, bcrypt, os

class UsersDB:
    def __init__(self, db_name):
        print("USER DB INIT", db_name)
        # self.db_name = db_name
        self.db_path = db_name

    def create_table(self):
        print("Se crea la tabla de usuarios")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def add_user(self, username, password):
        exists = self.get_user_by_username(username)
        if exists is None:
            print(f"Agregando {username} a la tabla usuarios")
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            conn.close()
            return True
        else:
            print(f"El usuario {username} ya existe en la base de datos!")
            return False

    def get_users(self):
        print("Retorna los usuarios")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM usuarios")
        users = [row[0] for row in cursor.fetchall()]
        conn.close()
        return users

    def get_user_by_username(self, username):
        print(f"Obteniendo info del usuario {username}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM usuarios WHERE username=?", (username,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            return {'username': user_data[0], 'password': user_data[1]}
        else:
            return None

    def recreate_database(self):
        print("Borrón y tabla de usuarios nueva")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Elimina la tabla si ya existe
        cursor.execute("DROP TABLE IF EXISTS usuarios")

        # Crea la tabla nuevamente
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        conn.commit()
        conn.close()

    def delete_user(self, username):
        print(f"Borrar usuario {username}")
        user_data = self.get_user_by_username(username)
        if user_data:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE username=?", (username,))
            conn.commit()
            conn.close()
            print("Eliminado correctamente")
            return True
        else:
            print(f"El usuario {username} no existe en la base de datos.")
            return False

    def update_password(self, username, new_hashed_password):
        user_data = self.get_user_by_username(username)
        if user_data:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET password = ? WHERE username = ?", (new_hashed_password, username))
            conn.commit()
            conn.close()
            print(f"Contraseña actualizada para el usuario {username}")
            return True
        else:
            print(f"El usuario {username} no existe en la base de datos.")
            return False

class RecordingsDB:
    def __init__(self, db_name):
        print("RECORDINGS DB INIT")
        self.db_path = db_name

    def create_table(self):
        print("Se crea tabla de recordings")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recordings (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                video_path TEXT NOT NULL,
                thumbnail_path TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def add_recording(self, name, video_path, thumbnail_path, created_at):
        print("Se agrega nueva recording con fecha", created_at)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO recordings (name, video_path, thumbnail_path, created_at) VALUES (?, ?, ?, ?)", (name, video_path, thumbnail_path, created_at))
        conn.commit()
        conn.close()

    def get_recordings(self):
        print("Obteniendo las grabaciones...")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recordings")
        recordings = cursor.fetchall()
        conn.close()
        return recordings

    def get_recording_by_name(self, name):
        print("Obteniendo grabación de nombre", name)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recordings WHERE name=?", (name,))
        recording_data = cursor.fetchone()
        conn.close()

        if recording_data:
            return {
                "name": recording_data[1],
                "video_path": recording_data[2],
                "thumbnail_path": recording_data[3],
                "created_at": recording_data[4]
            }
        else:
            return None

    def recreate_database(self):
        print("Borrón y tabla de recordings nueva")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Elimina la tabla si ya existe
        cursor.execute("DROP TABLE IF EXISTS recordings")

        # Crea la tabla nuevamente
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recordings (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                video_path TEXT NOT NULL,
                thumbnail_path TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')

        conn.commit()
        conn.close()

    def delete_recording(self, name):
        print("Borrando grabación de nombre", name)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM recordings WHERE name=?", (name,))
        conn.commit()
        conn.close()

    def update_recording(self, name, video_path, thumbnail_path, created_at):
        print("Actualizando grabación de nombre", name)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE recordings SET video_path=?, thumbnail_path=?, created_at=? WHERE name=?", (video_path, thumbnail_path, created_at, name))
        conn.commit()
        conn.close()

    def get_recordings_ordered_by_date(self):
        print("Obteniendo las grabaciones ordenadas por fecha...")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recordings ORDER BY created_at DESC")
        recordings = cursor.fetchall()
        conn.close()
        return recordings
