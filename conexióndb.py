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


def get_facial_descriptors_and_names_from_db():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT nombre, descriptores_faciales FROM estudiantes")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    # Convertir los descriptores faciales de bytes a arreglo NumPy y asociarlos con los nombres correspondientes
    descriptors_and_names = [(row[0], pickle.loads(row[1])) for row in rows]

    return descriptors_and_names








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
