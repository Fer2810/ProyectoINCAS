from flask import Flask, Response, json, render_template, request, redirect, url_for,jsonify
import mysql.connector
from camera import generate, start_camera,stop_camera
from conexióndb import create_connection, create_table, insert_usuario, close_connection, insert_estudiante, insert_administrador, send_email, authenticate_user, authenticate_userAdmin
from facial_recognition import extraer_encodings
from datetime import datetime
import pickle
import base64

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')



# Ruta para mostrar todas las secciones en tarjetas HTML
@app.route('/verSecciones')
def verSecciones():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_seccion, seccion, estado FROM secciones")
    secciones = cursor.fetchall()
    conn.close()
    return render_template('verSecciones.html', secciones=secciones)

@app.route('/toggleDeactivate', methods=['POST'])
def toggle_state():
    data = request.json
    seccion_id = data.get('id')
    state = data.get('state')
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE secciones SET estado = %s WHERE id_seccion = %s", (state, seccion_id))
        conn.commit()
        return jsonify({'message': 'Estado de la sección actualizado correctamente'}), 200
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
@app.route('/secciones/<string:seccion>')
def secciones(seccion):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_año, seccion, año, estado FROM años WHERE seccion = %s", (seccion,))
    años = cursor.fetchall()
    conn.close()
    return render_template('secciones.html', años=años)
        
        

@app.route('/toggleAnio', methods=['POST'])
def toggle_anio():
    data = request.get_json()
    seccion = data['seccion']
    anio = data['anio']
    new_state = data['state']

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE años SET estado = %s WHERE seccion = %s AND año = %s", (new_state, seccion, anio))
    conn.commit()
    conn.close()

    return jsonify(success=True)




@app.route('/toggleYears', methods=['POST'])
def toggle_years():
    data = request.json
    seccion_id = data.get('seccion_id')
    new_state = data.get('state')

    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Obtener la sección por id
        cursor.execute("SELECT seccion FROM secciones WHERE id_seccion = %s", (seccion_id,))
        seccion = cursor.fetchone()[0]

        # Actualizar el estado de los años de la sección
        cursor.execute("UPDATE años SET estado = %s WHERE seccion = %s", (new_state, seccion))
        conn.commit()
        return jsonify({'message': 'Estados de los años actualizados correctamente'}), 200
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
        
@app.route('/togglePresentes', methods=['POST'])
def toggle_presentes():
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Copiar los estudiantes a la tabla presentes si no existen
        cursor.execute("""
            INSERT INTO presentes (nie, nombre, apellido, correo_electronico, genero, bachillerato, imagen, descriptores_faciales, id_año)
            SELECT nie, nombre, apellido, correo_electronico, genero, bachillerato, imagen, descriptores_faciales, id_año
            FROM estudiantes
            WHERE id_año IN (SELECT id_año FROM años WHERE estado = '1')
            ON DUPLICATE KEY UPDATE
                nombre=VALUES(nombre), apellido=VALUES(apellido), correo_electronico=VALUES(correo_electronico),
                genero=VALUES(genero), bachillerato=VALUES(bachillerato), imagen=VALUES(imagen),
                descriptores_faciales=VALUES(descriptores_faciales), id_año=VALUES(id_año)
        """)

        conn.commit()
        return jsonify({'message': 'Copia de estudiantes realizada correctamente'}), 200
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
        
@app.route('/clearPresentes', methods=['POST'])
def clear_presentes():
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Vaciar la tabla presentes
        cursor.execute("DELETE FROM presentes")

        conn.commit()
        return jsonify({'message': 'Tabla presentes vaciada correctamente'}), 200
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
        
# Ruta para manejar la solicitud POST desde el cliente
@app.route('/guardar_estudiantes', methods=['POST'])
def guardar_estudiantes():
    student_data = request.form['studentData']
    students = json.loads(student_data)

    # Insertar los datos de todos los estudiantes en la base de datos
    for student in students:
        sql = "INSERT INTO estudiantes (nie, nombre, bachillerato, fecha, hora) VALUES (%s, %s, %s, %s, %s)"
        val = (student['nie'], student['nombre'], student['bachillerato'], student['fecha'], student['hora'])
        create_connection.execute(sql, val)
    create_connection.commit()

    return 'Datos de estudiantes guardados en la base de datos'
        
        
# Ruta para imprimir en la terminal las secciones activas
@app.route('/print_active_sections', methods=['POST'])
def print_active_sections():
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id_seccion, seccion FROM secciones WHERE estado = 'activa'")
        active_sections = cursor.fetchall()
        for section in active_sections:
            print(f"ID: {section[0]}, Sección: {section[1]}")
        return '', 204
    except Exception as e:
        print("Error:", e)
        return str(e), 500
    finally:
        conn.close()


# Tu código Flask para obtener los datos binarios de la imagen de la base de datos
@app.route('/formuA')
def mostrar_registros():
    # Conectar a la base de datos y obtener un cursor
    db = create_connection()
    cursor = db.cursor()

    # Ejecutar una consulta SQL para seleccionar todos los registros de tu tabla
    cursor.execute("SELECT id_administrador, nombre, apellidos, correo, imagen FROM administradores")
    # Obtener todos los registros
    registros = cursor.fetchall()

    # Convertir los datos binarios de la imagen a cadena base64
    registros_con_imagen_base64 = []
    for registro in registros:
        id_administrador = registro[0]
        nombre = registro[1]
        apellidos = registro[2]
        correo = registro[3]
        imagen_binaria = registro[4]
        imagen_base64 = base64.b64encode(imagen_binaria).decode('utf-8')
        registros_con_imagen_base64.append((id_administrador, nombre, apellidos, correo, imagen_base64))

    # Cerrar el cursor y la conexión
    cursor.close()
    db.close()

    # Renderizar la plantilla HTML y pasar los registros como contexto
    return render_template('formuA.html', registros=registros_con_imagen_base64)

@app.route('/editar_administrador/<int:id_administrador>', methods=['GET', 'POST'])
def editar_administrador(id_administrador):
    conn = create_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        correo = request.form['correo']
        imagen = request.files['imagen'].read() if request.files['imagen'] else None

        # Actualizar los datos del administrador en la base de datos
        if imagen:
            cursor.execute("UPDATE administradores SET nombre=%s, apellidos=%s, correo=%s, imagen=%s WHERE id_administrador=%s",
                           (nombre, apellidos, correo, imagen, id_administrador))
        else:
            cursor.execute("UPDATE administradores SET nombre=%s, apellidos=%s, correo=%s WHERE id_administrador=%s",
                           (nombre, apellidos, correo, id_administrador))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('mostrar_registros'))

    cursor.execute("SELECT id_administrador, nombre, apellidos, correo FROM administradores WHERE id_administrador=%s", (id_administrador,))
    administrador = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('editar_administrador.html', administrador=administrador)

@app.route('/eliminar_administrador', methods=['POST'])
def eliminar_administrador():
    if request.method == 'POST':
        # Obtener el ID del administrador a eliminar desde el formulario
        id_administrador = request.form['id_administrador']

        # Conectar a la base de datos
        conn = create_connection()
        cursor = conn.cursor()

        try:
            # Ejecutar la consulta SQL para eliminar al administrador
            cursor.execute("DELETE FROM administradores WHERE id_administrador = %s", (id_administrador,))
            conn.commit()
            return redirect(url_for('mostrar_registros'))
        except Exception as e:
            # Manejar cualquier error que ocurra durante la eliminación
            return f'Error al eliminar el administrador: {str(e)}'
        finally:
            cursor.close()
            conn.close()


@app.route('/editar_profesor/<int:id_profesor>', methods=['GET', 'POST'])
def editar_profesor(id_profesor):
    conn = create_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        imagen = request.files['imagen'].read() if request.files['imagen'] else None

        # Actualizar los datos del profesor en la base de datos
        if imagen:
            cursor.execute("UPDATE Datos_Prof SET nombre=%s, apellido=%s, email=%s, imagen=%s WHERE nip=%s",
                           (nombre, apellido, email, imagen, id_profesor))
        else:
            cursor.execute("UPDATE Datos_Prof SET nombre=%s, apellido=%s, email=%s WHERE nip=%s",
                           (nombre, apellido, email, id_profesor))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('formuP'))

    cursor.execute("SELECT nip, nombre, apellido, email, imagen FROM Datos_Prof WHERE nip=%s", (id_profesor,))
    profesor = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('editar_profesor.html', profesor=profesor)

@app.route('/eliminar_profesor', methods=['POST'])
def eliminar_profesor():
    if request.method == 'POST':
        # Obtener el ID del profesor a eliminar desde el formulario
        id_profesor = request.form['id_profesor']

        # Conectar a la base de datos
        conn = create_connection()
        cursor = conn.cursor()

        try:
            # Ejecutar la consulta SQL para eliminar al profesor
            cursor.execute("DELETE FROM Datos_Prof WHERE nip = %s", (id_profesor,))
            conn.commit()
            return redirect(url_for('formuP'))
        except Exception as e:
            # Manejar cualquier error que ocurra durante la eliminación
            return f'Error al eliminar el profesor: {str(e)}'
        finally:
            cursor.close()
            conn.close()



@app.route('/indexPersonal')
def indexPersonal():
  return render_template('indexPersonal.html')

@app.route('/cursos')
def cursos():
  return render_template('cursos.html')

@app.route('/seccion')
def seccion():
  return render_template('seccion.html')

@app.route('/formuP')
def formuP():
    # Conectar a la base de datos y obtener un cursor
    conn = create_connection()
    cursor = conn.cursor()

    try:
        # Ejecutar una consulta SQL para seleccionar todos los registros de profesores
        cursor.execute("SELECT nip, nombre, apellido, email, imagen FROM Datos_Prof")
        # Obtener todos los registros
        profesores = cursor.fetchall()
    except Exception as e:
        print("Error al obtener datos de profesores:", e)
        profesores = []

    # Cerrar el cursor y la conexión
    cursor.close()
    conn.close()

    # Convertir los datos binarios de la imagen a cadena base64
    registros_con_imagen_base64 = []
    for profesor in profesores:
        id_profesor = profesor[0]
        nombre = profesor[1]
        apellido = profesor[2]
        email = profesor[3]
        imagen_binaria = profesor[4]
        imagen_base64 = base64.b64encode(imagen_binaria).decode('utf-8')
        registros_con_imagen_base64.append((id_profesor, nombre, apellido, email, imagen_base64))

    # Renderizar la plantilla HTML y pasar los registros como contexto
    return render_template('formuP.html', profesores=registros_con_imagen_base64)



@app.route('/recup')
def recup():
  return render_template('recuperacion.html')

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

@app.route('/AdmiEstu')
def AdmiEstu():
  return render_template('AdmiEstu.html')


@app.route('/buscar_estudiantes', methods=['GET'])
def buscar_estudiantes():
    id_año = request.args.get('id_año')
    
    if id_año is None:
        return jsonify([])  # Devuelve una lista vacía si no se proporciona id_año

    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT nie, nombre, apellido, correo_electronico, genero, bachillerato, imagen, id_año FROM estudiantes WHERE id_año = %s", (id_año,))
    estudiantes = cursor.fetchall()
    
    registros = []
    for estudiante in estudiantes:
        nie = estudiante[0]
        nombre = estudiante[1]
        apellido = estudiante[2]
        correo_electronico = estudiante[3]
        genero = estudiante[4]
        bachillerato = estudiante[5]
        imagen_binaria = estudiante[6]
        imagen_base64 = base64.b64encode(imagen_binaria).decode('utf-8') if imagen_binaria else None
        id_año = estudiante[7]
        registros.append({
            'nie': nie,
            'nombre': nombre,
            'apellido': apellido,
            'correo_electronico': correo_electronico,
            'genero': genero,
            'bachillerato': bachillerato,
            'imagen': imagen_base64,
            'id_año': id_año
        })

    cursor.close()
    conn.close()
    
    return jsonify(registros)


@app.route('/editar_estudiante/<int:nie>', methods=['GET', 'POST'])
def editar_estudiante(nie):
    conn = create_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Obtener datos del formulario
        imagen = request.files['imagen'].read() if request.files['imagen'] else None
        nie_edit = request.form['nie_edit']  # Nuevo campo para editar el NIE
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        genero = request.form['genero']
        bachillerato = request.form['bachillerato']

        # Extraer los descriptores faciales
        encoding_imagen = extraer_encodings(imagen)

        if imagen and encoding_imagen is not None:
            cursor.execute("UPDATE estudiantes SET imagen=%s, descriptores_faciales=%s, nombre=%s, apellido=%s, correo_electronico=%s, genero=%s, bachillerato=%s, nie=%s WHERE nie=%s",
                           (imagen, pickle.dumps(encoding_imagen), nombre, apellido, email, genero, bachillerato, nie_edit, nie))
            conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for('AdmiEstu'))

    cursor.execute("SELECT nombre, apellido, nie, correo_electronico, genero, bachillerato FROM estudiantes WHERE nie=%s", (nie,))
    estudiante = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('editar_estudiante.html', estudiante=estudiante, nie=nie)



@app.route('/get_años', methods=['GET'])
def get_años():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_año FROM años")
    años = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([{"id_año": año[0]} for año in años])

@app.route('/update_estudiantes', methods=['POST'])
def update_estudiantes():
    updates = request.json  # Obtener los datos JSON enviados desde el frontend
    conn = create_connection()
    cursor = conn.cursor()

    try:
        for update in updates:
            nie = update['nie']
            id_año = update['id_año']
            cursor.execute("UPDATE estudiantes SET id_año = %s WHERE nie = %s", (id_año, nie))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error updating students: {e}")
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/eliminar_estudiante/<int:nie>', methods=['DELETE'])
def eliminar_estudiante(nie):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM estudiantes WHERE nie = %s", (nie,))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error deleting student: {e}")
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()
        conn.close()




# Ruta para la página de inicio de cámara
@app.route('/starf', methods=['GET', 'POST'])
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

# Ruta para el feed de video
@app.route("/student_info")
def student_info():
    return Response(generate(), mimetype="text/event-stream")

@app.route('/pin')
def pin():
  return render_template('pin.html')

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
        imagen = request.files['imagen'].read()
        
        # Conectar a la base de datos
        conn = create_connection()
        create_table(conn)

        # Insertar datos en la base de datos
        insert_usuario(conn, nombre, apellido, nip, email, imagen)

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
                return render_template('recuperacion.html', mensaje=mensaje)
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
    conn = create_connection()
    cursor = conn.cursor()

    # Obtener los id_año de la tabla años
    cursor.execute("SELECT id_año FROM años")
    años = cursor.fetchall()

    # Cerrar la conexión
    cursor.close()
    conn.close()

    # Pasar los id_año a la plantilla
    return render_template('estudiante.html', años=años)



@app.route('/submit_estudiante', methods=['POST'])
def submit_estudiante():
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        correo_electronico = request.form['correo_electronico']
        genero = request.form['genero']
        nie = request.form['nie']
        bachillerato = request.form['bachillerato']
        id_año = request.form['id_año']  # Obtener el id_año del formulario
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
                insert_estudiante(conn, nombre, apellido, correo_electronico, genero, nie, bachillerato, imagen_bytes, encoding_imagen, id_año)

                # Cerrar la conexión
                close_connection(conn)

                return 'Datos enviados a la base de datos y correo electrónico enviado con éxito'
            except Exception as e:
                return f'Error al procesar y almacenar la imagen: {str(e)}'
        else:
            return 'No se detectaron caras en la imagen. Intente con otra imagen.'




def insert_estudiante(conn, nombre, apellido, correo_electronico, genero, nie, bachillerato, imagen_bytes, encoding_imagen, id_año):
    cursor = conn.cursor()
    # Convertir el arreglo NumPy a bytes usando pickle
    encoding_bytes = pickle.dumps(encoding_imagen)
    cursor.execute("INSERT INTO estudiantes (nombre, apellido, correo_electronico, genero, nie, bachillerato, imagen, descriptores_faciales, id_año) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                   (nombre, apellido, correo_electronico, genero, nie, bachillerato, imagen_bytes, encoding_bytes, id_año))
    conn.commit()
    cursor.close()


# Ruta para procesar los datos del formulario de sección
@app.route('/submit_seccion', methods=['POST'])
def submit_seccion():
    if request.method == 'POST':
        # Obtener datos del formulario
        id_seccion = request.form['id_seccion']
        seccion = request.form['seccion']
        

        try:
            # Conectar a la base de datos
            conn = create_connection()
            create_table(conn)  # Asegúrate de que la tabla exista

            # Insertar datos en la base de datos
            insert_seccion(conn, id_seccion, seccion, )

            # Cerrar la conexión
            close_connection(conn)

            return 'Datos de sección enviados a la base de datos correctamente'
        except Exception as e:
            return f'Error al procesar y almacenar los datos de la sección: {str(e)}'

def insert_seccion(conn, id_seccion, seccion):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO secciones (id_seccion, seccion) VALUES (%s, %s)",
                   (id_seccion, seccion))
    conn.commit()
    cursor.close()

@app.route('/CrearAño')
def crear_año():
    # Conectar a la base de datos y obtener un cursor
    conn = create_connection()
    cursor = conn.cursor()

    try:
        # Ejecutar una consulta SQL para seleccionar todas las secciones
        cursor.execute("SELECT seccion FROM secciones")
        # Obtener todas las secciones y convertirlas en una lista de cadenas de texto
        secciones = [seccion[0] for seccion in cursor.fetchall()]
    except Exception as e:
        # Manejar cualquier error que ocurra al obtener las secciones
        print("Error al obtener las secciones:", e)
        secciones = []

    # Cerrar el cursor y la conexión
    cursor.close()
    conn.close()

    # Renderizar la plantilla HTML y pasar las secciones como contexto
    return render_template('CrearAño.html', secciones=secciones)


# Ruta para procesar los datos del formulario de año
@app.route('/submit_año', methods=['POST'])
def submit_año():
    if request.method == 'POST':
        # Obtener datos del formulario
        id_año = request.form['id_año']
        año = request.form['año']
        seccion = request.form['seccion']

        try:
            # Conectar a la base de datos
            conn = create_connection()
            create_table(conn)  # Asegúrate de que la tabla exista

            # Insertar datos en la base de datos
            insert_año(conn, id_año, año, seccion)

            # Cerrar la conexión
            close_connection(conn)

            return 'Datos del año enviados a la base de datos correctamente'
        except Exception as e:
            return f'Error al procesar y almacenar los datos del año: {str(e)}'

def insert_año(conn, id_año, año, seccion):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO años (id_año, año, seccion) VALUES (%s, %s, %s)",
                   (id_año, año, seccion))
    conn.commit()
    cursor.close()
    
    
    
    
    
    
    
    
    
    



@app.route('/EditarSeccion')
def EditarSeccion():
  return render_template('EditarSeccion.html')

@app.route('/EditarAño')
def EditarAño():
  return render_template('EditarAño.html')

if __name__ == '__main__':
  app.run(debug=True)