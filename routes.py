from flask import Flask, Response, render_template, request, redirect, url_for
from camera import generate, start_camera,stop_camera
from conexióndb import create_connection, create_table, insert_usuario, close_connection, insert_estudiante, insert_administrador, send_email, authenticate_user, authenticate_userAdmin
from facial_recognition import extraer_encodings
from datetime import datetime
import pickle


app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/login')
def login():
  return render_template('login.html')

@app.route('/loginAdmin')
def loginAdmin():
  return render_template('loginAdmin.html')

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/profesor')
def profesor():
  return render_template('profesor.html')


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


@app.route('/inicio')
def inicio():
  return render_template('inicio.html')
  

@app.route('/masRecursos')
def masRecursos():
  return render_template('masRecursos.html')

@app.route('/ayuda')
def ayuda():
  return render_template('ayuda.html')

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
    imagen = request.files['imagen'].read()

    # Conectar a la base de datos
    conn = create_connection()
    create_table(conn)

    # Insertar datos en la base de datos
    insert_usuario(conn, nombre, apellido, nip, email, id_docente, imagen)

    # Cerrar la conexión
    close_connection(conn)

    return 'Datos enviados a la base de datos y correo electrónico enviado con éxito'
  

@app.route('/loginn', methods=['POST'])
def loginn():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['contraseña']

        user = authenticate_user(email, password)

        if user:
            # Inicio de sesión exitoso, redireccionar a una página de bienvenida
            return redirect(url_for('about'))
        else:
            # Credenciales incorrectas, redireccionar de nuevo al formulario de inicio de sesión
            return render_template('login.html', error="Credenciales incorrectas")
  

@app.route('/getPassword')
def getPassword():
  return render_template('getPassword.html')
  

@app.route('/recuperacion', methods=['GET', 'POST'])
def recuperacion():
    if request.method == 'POST':
        email = request.form['email']

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT contraseña FROM Datos_Prof WHERE email = %s", (email,))
        contraseña_encontrada = cursor.fetchone()

        if contraseña_encontrada:
            # Enviar la contraseña tal como está en la base de datos por correo electrónico
            message = f"Tu contraseña es: {contraseña_encontrada[0]}"
            if send_email(email, message):
                mensaje = "Revisa tu correo electronico" 
                return render_template('login.html', mensaje=mensaje)
            else:
                return "Error al enviar correo electrónico. Por favor, inténtelo de nuevo más tarde."
        else:
            return "No se encontró ninguna cuenta asociada a ese correo electrónico."

    return render_template('get_password.html')

  

@app.route('/administrador')
def administrador():
  return render_template('administrador.html')

# Ruta para procesar los datos del formulario de administrador
@app.route('/admin_form', methods=['POST'])
def submit_admin_form():
    if request.method == 'POST':
        # Obtener datos del formulario
        id_administrador = request.form['id_administrador']
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        correo = request.form['correo']
        imagen = request.files['imagen'].read()  # Lee el contenido del archivo de imagen
        
        # Conectar a la base de datos
        conn = create_connection()
        create_table(conn)  # Asegúrate de que la tabla exista

        # Insertar datos en la base de datos
        insert_administrador(conn, id_administrador, nombre, apellidos, correo, imagen)

        # Cerrar la conexión
        close_connection(conn)

        return 'Datos del administrador enviados a la base de datos y correo electrónico enviado con éxito'
      

@app.route('/getPasswordAdmin')
def getPasswordAdmin():
  return render_template('getPasswordAdmin.html')


@app.route('/loginnAdmin', methods=['POST'])
def loginnAdmin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['contraseña']

        user = authenticate_userAdmin(email, password)

        if user:
            # Inicio de sesión exitoso, redireccionar a una página de bienvenida
            return redirect(url_for('about'))
        else:
            # Credenciales incorrectas, redireccionar de nuevo al formulario de inicio de sesión
            return redirect(url_for)('loginnAdmin', error = "Credenciale no coinciden")

@app.route('/recuperacionAdmin', methods=['GET', 'POST'])
def recuperacionAdmin():
    if request.method == 'POST':
        email = request.form['email']

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT contraseña FROM administradores WHERE correo = %s", (email,))
        contraseña_encontrada = cursor.fetchone()

        if contraseña_encontrada:
            # Enviar la contraseña tal como está en la base de datos por correo electrónico
            message = f"Tu contraseña es: {contraseña_encontrada[0]}"
            if send_email(email, message):
                mensaje = "Revisa tu correo electronico" 
                return render_template('loginAdmin.html', mensaje=mensaje)
            else:
                return "Error al enviar correo electrónico. Por favor, inténtelo de nuevo más tarde."
        else:
            return "No se encontró ninguna cuenta asociada a ese correo electrónico."

    return render_template('get_password.html')


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


if __name__ == '__main__':
  app.run(debug=True)

