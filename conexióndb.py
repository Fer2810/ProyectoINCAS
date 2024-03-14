import mysql.connector
import bcrypt
import random
import string
import pickle


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


##################################################################################################################



def insert_estudiante(conn, nombre, apellido, correo_electronico, genero, nit, bachillerato, imagen_bytes, encoding_imagen):
    try:
        cursor = conn.cursor()

        # Convertir los descriptores faciales de numpy.ndarray a bytes
        encoding_bytes = pickle.dumps(encoding_imagen)

        # Consulta SQL para insertar un estudiante en la tabla Estudiantes
        insert_query = """
        INSERT INTO estudiantes (nombre, apellido, correo_electronico, genero, nit, bachillerato, imagen, descriptores_faciales)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Datos a insertar en la tabla
        data = (nombre, apellido, correo_electronico, genero, nit, bachillerato, imagen_bytes, encoding_bytes)

        # Ejecutar la consulta SQL
        cursor.execute(insert_query, data)

        # Confirmar los cambios en la base de datos
        conn.commit()
        print("Datos de estudiante insertados correctamente.")
    except mysql.connector.Error as e:
        print("Error al insertar datos de estudiante:", e)
        
        
        
        
##################################################################################################################
        
        
        
        
        
        
        
           
def insert_administrador(conn, id_administrador, nombre, apellidos, correo, imagen):
    cursor = conn.cursor()
    password = generate_random_password()
    hashed_password = hash_password(password)
    sql = '''INSERT INTO Administradores (id_administrador, nombre, apellidos, correo, imagen, contraseña_hash) VALUES (%s, %s, %s, %s, %s, %s)'''
    values = (id_administrador, nombre, apellidos, correo, imagen, hashed_password)
    cursor.execute(sql, values)
    conn.commit()
    return password

def insert_materia(conn, subject_name, subject_id):
    cursor = conn.cursor()
    sql = '''INSERT INTO Materias (nombre_materia, id_materia) VALUES (%s, %s)'''
    values = (subject_name, subject_id)
    cursor.execute(sql, values)
    conn.commit()

def close_connection(conn):
    conn.close()
