import mysql.connector
import bcrypt
import random
import string

def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="app_incas"
    )

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Datos_Prof (
                    id_docente VARCHAR(255) NOT NULL PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    apellido VARCHAR(255) NOT NULL,
                    nip VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    imagen LONGBLOB NOT NULL,
                    contraseña_hash VARCHAR(255) NOT NULL
                )''')
    conn.commit()

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def hash_password(password):
    # Generar un salt aleatorio
    salt = bcrypt.gensalt()
    # Hashear la contraseña con el salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def insert_usuario(conn, nombre, apellido, nip, email, id_docente, imagen):
    cursor = conn.cursor()
    password = generate_random_password()
    hashed_password = hash_password(password)
    sql = '''INSERT INTO Datos_Prof (nombre, apellido, nip, email, id_docente, imagen, contraseña_hash) VALUES (%s, %s, %s, %s, %s, %s, %s)'''
    values = (nombre, apellido, nip, email, id_docente, imagen, hashed_password)
    cursor.execute(sql, values)
    conn.commit()
    return password

def close_connection(conn):
    conn.close()

 