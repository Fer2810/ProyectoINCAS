
from flask import Flask, render_template, request
from conexióndb import create_connection, create_table, insert_usuario, close_connection, insert_estudiante, insert_administrador
from facial_recognition import extraer_encodings

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

@app.route('/reconocimiento')
def reconocimiento():
  return render_template('reconocimiento.html')

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




if __name__ == '__main__':
  app.run(debug=True)

