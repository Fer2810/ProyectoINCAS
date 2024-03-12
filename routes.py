from flask import Flask, render_template, request
from conexióndb import create_connection, create_table, insert_usuario, close_connection, insert_administrador, insert_materia

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

@app.route('/Materia')
def Materia():
    
    return render_template('Materia.html')

# Ruta para procesar los datos del formulario de materia
@app.route('/Materia', methods=['POST'])
def submit_materia():
    if request.method == 'POST':
        # Obtener datos del formulario
        subject_name = request.form['subject_name']
        subject_id = request.form['subject_id']
        
        # Conectar a la base de datos
        conn = create_connection()
        create_table(conn)  # Asegúrate de que la tabla exista

        # Insertar datos en la base de datos
        insert_materia(conn, subject_name, subject_id)

        # Cerrar la conexión
        close_connection(conn)

        return 'Materia guardada exitosamente'


if __name__ == '__main__':
    app.run(debug=True)
