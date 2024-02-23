from flask import Flask, render_template, request
from conexióndb import create_connection, create_table, insert_usuario, close_connection

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

        return 'Datos enviados a la base de datos con éxito'

@app.route('/administrador')
def administrador():
    return render_template('administrador.html')

if __name__ == '__main__':
    app.run(debug=True)
