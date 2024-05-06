import mysql.connector
import random
import string
import pickle
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# Configuración del servidor SMTP de Gmail
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
GMAIL_USERNAME = 'fernandotb281005@gmail.com'  # Tu dirección de correo electrónico de Gmail
GMAIL_PASSWORD = 'qtal sejm zvqs uuua'  # Tu contraseña de Gmail

def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="appstarf"
    )



def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Datos_Prof (
                    nip int(255) NOT NULL PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    apellido VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    imagen LONGBLOB NOT NULL,
                    contraseña VARCHAR(255) NOT NULL
                )''')
    conn.commit()

def insert_usuario(conn, nombre, apellido, nip, email, imagen):
    cursor = conn.cursor()
    password = generate_random_password()  # Generar una contraseña aleatoria
    sql = '''INSERT INTO Datos_Prof (nombre, apellido, nip, email, imagen, contraseña) VALUES (%s, %s, %s, %s, %s, %s)'''
    values = (nombre, apellido, nip, email,  imagen, password)
    cursor.execute(sql, values)
    conn.commit()
    return password


def insert_administrador(conn, id_administrador, nombre, apellidos, correo, imagen):
    cursor = conn.cursor()
    password = generate_random_password()  # Generar una contraseña aleatoria
    sql = '''INSERT INTO Administradores (id_administrador, nombre, apellidos, correo, imagen, contraseña) VALUES (%s, %s, %s, %s, %s, %s)'''
    values = (id_administrador, nombre, apellidos, correo, imagen, password)
    cursor.execute(sql, values)
    conn.commit()
    return password


def authenticate_userAdmin(email, password):
    conn = create_connection()  # Llama a la función create_connection para obtener los valores de configuración
    cursor = conn.cursor()

    # Consulta para verificar las credenciales del usuario
    query = "SELECT id_administrador FROM administradores WHERE correo = %s AND contraseña = %s"
    cursor.execute(query, (email, password))
    user = cursor.fetchone()

    conn.close()

    return user


def authenticate_user(email, password):
    conn = create_connection()  # Llama a la función create_connection para obtener los valores de configuración
    cursor = conn.cursor()

    # Consulta para verificar las credenciales del usuario
    query = "SELECT id_docente FROM Datos_Prof WHERE email = %s AND contraseña = %s"
    cursor.execute(query, (email, password))
    user = cursor.fetchone()

    conn.close()

    return user


def send_email(to_email, message):
    try:
        # Configurar conexión SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(GMAIL_USERNAME, GMAIL_PASSWORD)

        # Crear mensaje de correo
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USERNAME
        msg['To'] = to_email
        msg['Subject'] = 'Contraseña recuperada'

        # Agregar el cuerpo del mensaje
        msg.attach(MIMEText(message, 'plain'))

        # Enviar correo electrónico
        server.sendmail(GMAIL_USERNAME, to_email, msg.as_string())

        # Cerrar conexión SMTP
        server.quit()
        return True
    except Exception as e:
        print("Error al enviar correo electrónico:", e)
        return False


def get_facial_descriptors_and_names_from_db():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT nit ,nombre, bachillerato, descriptores_faciales FROM estudiantes")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    # Convertir los descriptores faciales de bytes a arreglo NumPy y asociarlos con los nombres correspondientes
    student_data = [(row[0], row[1], row[2], pickle.loads(row[3])) for row in rows]

    return student_data

        

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))



def insert_estudiante(conn, nombre, apellido, correo_electronico, genero, nit, bachillerato, imagen_bytes, encoding_imagen, seccion):
    try:
        cursor = conn.cursor()

        # Convertir los descriptores faciales de numpy.ndarray a bytes
        encoding_bytes = pickle.dumps(encoding_imagen)

        # Consulta SQL para insertar un estudiante en la tabla Estudiantes
        insert_query = """
        INSERT INTO estudiantes (nombre, apellido, correo_electronico, genero, nit, bachillerato, imagen, descriptores_faciales, seccion)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Datos a insertar en la tabla
        data = (nombre, apellido, correo_electronico, genero, nit, bachillerato, imagen_bytes, encoding_bytes, seccion)

        # Ejecutar la consulta SQL
        cursor.execute(insert_query, data)

        # Confirmar los cambios en la base de datos
        conn.commit()
        print("Datos de estudiante insertados correctamente.")
    except mysql.connector.Error as e:
        print("Error al insertar datos de estudiante:", e)



def close_connection(conn):
    conn.close()
