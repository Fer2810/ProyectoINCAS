import mysql.connector
import random
import string
from flask import Flask, request, jsonify
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'fernandotb281005@gmail.com'  # Ingresa tu dirección de correo electrónico
app.config['MAIL_PASSWORD'] = 'dxeu hvgv zwsb gtju'  # Ingresa tu contraseña de correo electrónico

mail = Mail(app)

def create_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="app_incas",
        # Configuración para el tamaño máximo del paquete
        connection_timeout=300,
        max_allowed_packet=1073741824  # 1GB (en bytes)
    )
    return conn

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                    id_docente VARCHAR(255) PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    apellido VARCHAR(255) NOT NULL,
                    nip VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    imagen LONGBLOB NOT NULL,
                    contraseña VARCHAR(20) NOT NULL,
                    UNIQUE (email)
                )''')
    conn.commit()

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def send_email(to_email, nombre, password):
    msg = Message('Contraseña Generada', sender='fernandotb281005@gmail.com', recipients=[to_email])
    msg.body = f'Hola {nombre},\n\nSe ha generado una contraseña para tu cuenta. Tu nueva contraseña es: {password}\n\nSaludos,\nEl equipo de tu aplicación'
    mail.send(msg)

def insert_usuario(conn, nombre, apellido, nip, email, id_docente, imagen):
    cursor = conn.cursor()
    password = generate_random_password()
    sql = '''INSERT INTO usuarios (nombre, apellido, nip, email, id_docente, imagen, contraseña) VALUES (%s, %s, %s, %s, %s, %s, %s)'''
    values = (nombre, apellido, nip, email, id_docente, imagen, password)
    cursor.execute(sql, values)
    conn.commit()
    send_email(email, nombre, password)

def close_connection(conn):
    conn.close()

@app.route('/crear_usuario', methods=['POST'])
def crear_usuario():
    try:
        nombre = request.json['nombre']
        apellido = request.json['apellido']
        nip = request.json['nip']
        email = request.json['email']
        id_docente = request.json['id_docente']
        imagen = request.json['imagen']

        conn = create_connection()
        create_table(conn)
        insert_usuario(conn, nombre, apellido, nip, email, id_docente, imagen)
        close_connection(conn)

        response = {'message': 'Usuario creado exitosamente'}
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
