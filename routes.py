import subprocess
from flask import Flask, Response, render_template, request

from camera import generate, start_camera,stop_camera

from conexióndb import create_connection, create_table, insert_usuario, close_connection, insert_estudiante, insert_materia, insert_administrador

from facial_recognition import extraer_encodings

import pickle




app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/profesor')
def profesor():
    return render_template('profesor.html')

@app.route('/inicio')
def inicio():
    return render_template('inicio.html')


###############################################################################################

# Ruta para la página de inicio de cámara
@app.route('/starf.html', methods=['GET', 'POST'])
def starf():
    if request.method == 'POST':
        if request.form['action'] == 'start_camera':
            start_camera()
        elif request.form['action'] == 'stop_camera':
            stop_camera()

    return render_template('starf.html')

# Ruta para el feed de video
@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route('/estudiante')
def estudiante():
  return render_template('estudiante.html')

# Ruta para procesar los datos del formulario de registro de estudiante
@app.route('/submit_estudiante', methods=['POST'])
def submit_estudiante():
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        correo_electronico = request.form['correo_electronico']
        genero = request.form['genero']
        nit = request.form['nit']
        bachillerato = request.form['bachillerato']
        imagen = request.files['imagen']  # Obtener la imagen del formulario
        imagen_bytes = imagen.read()  # Leer los bytes de la imagen

        # Extraer los encodings de la imagen
        encoding_imagen = extraer_encodings(imagen_bytes)

        if encoding_imagen is not None:
            try:
                # Conectar a la base de datos
                conn = create_connection()
                create_table(conn)  # Asegúrate de que la tabla exista

                # Insertar datos en la base de datos
                insert_estudiante(conn, nombre, apellido, correo_electronico, genero, nit, bachillerato, imagen_bytes, encoding_imagen)
                
                # Cerrar la conexión
                close_connection(conn)

                return 'Datos enviados a la base de datos y correo electrónico enviado con éxito'
            except Exception as e:
                return f'Error al procesar y almacenar la imagen: {str(e)}'
        else: 
            return 'No se detectaron caras en la imagen. Intente con otra imagen.'

def insert_estudiante(conn, nombre, apellido, correo_electronico, genero, nit, bachillerato, imagen_bytes, encoding_imagen):
    cursor = conn.cursor()
    # Convertir el arreglo NumPy a bytes usando pickle
    encoding_bytes = pickle.dumps(encoding_imagen)
    cursor.execute("INSERT INTO estudiantes (nombre, apellido, correo_electronico, genero, nit, bachillerato, imagen, descriptores_faciales) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                   (nombre, apellido, correo_electronico, genero, nit, bachillerato, imagen_bytes, encoding_bytes))
    conn.commit()
    cursor.close()



###############################################################################################################










# Ruta para procesar los datos del formulario
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        nip = request.form['nip']
        email = request.form['email']
        id_docente = request.form['id_docente']
        imagen = request.files['imagen'].read()  # Lee el contenido del archivo de imagen

        # Conectar a la base de datos
        conn = create_connection()
        create_table(conn)  # Asegúrate de que la tabla exista

        # Insertar datos en la base de datos
        insert_usuario(conn, nombre, apellido, nip, email, id_docente, imagen)

        # Cerrar la conexión
        close_connection(conn)

        return 'Datos enviados a la base de datos y correo electrónico enviado con éxito'

@app.route('/administrador')
def administrador():
    return render_template('administrador.html')




if __name__ == '__main__':
    app.run(debug=True)
 