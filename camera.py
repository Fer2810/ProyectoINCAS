import cv2
import dlib
import numpy as np
import mysql.connector
from flask import Flask, Response
from scipy.spatial import distance
import pickle
import threading

app = Flask(__name__)

# Función para crear la conexión a la base de datos
def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="app_incas"
    ) 

# Función para obtener los descriptores faciales de la base de datos
def get_facial_descriptors_from_db():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT descriptores_faciales FROM estudiantes")
    descriptors = cursor.fetchall()
    cursor.close()
    connection.close()
    
    # Convertir los descriptores faciales de bytes a arreglo NumPy
    descriptors_np = [pickle.loads(descriptor[0]) for descriptor in descriptors]
    
    return descriptors_np

# Cargar el modelo de predicción facial de dlib
predictor = dlib.shape_predictor("env/Lib/site-packages/dlib/models/shape_predictor_68_face_landmarks.dat")
facial_recognition_model = dlib.face_recognition_model_v1("env/Lib/site-packages/dlib/models/dlib_face_recognition_resnet_model_v1.dat")

# Inicializar el detector de caras de dlib
detector = dlib.get_frontal_face_detector()
cap = None
camera_running = False

# Variable para almacenar los descriptores faciales de la base de datos
descriptors_from_db = get_facial_descriptors_from_db()

# Umbral para la comparación de distancias
umbral = 0.7  # Puedes ajustar este valor según tus necesidades

# Variable para almacenar el resultado de la comparación
last_result = None

# Variable para almacenar los descriptores faciales del primer rostro detectado
first_frame_descriptors = None

# Función para iniciar la cámara
def start_camera():
    global cap, camera_running
    if not camera_running:
        cap = cv2.VideoCapture(0)
        camera_running = True

# Función para detener la cámara
def stop_camera():
    global cap, camera_running
    if camera_running:
        cap.release()
        camera_running = False

# Función para procesar el video
# Función para procesar el video
def generate():
    global first_frame_descriptors, last_result
    while camera_running:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Error al capturar el frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        caras = detector(gray)

        # Verificar si se ha reiniciado la cámara
        if not last_result:
            first_frame_descriptors = None

        # Actualizar los descriptores faciales de la base de datos en cada iteración
        descriptors_from_db = get_facial_descriptors_from_db()

        # Verificar si es el primer rostro detectado y compararlo con los descriptores de la base de datos
        if first_frame_descriptors is None:
            if len(caras) > 0:
                # Extraer descriptores faciales del primer rostro detectado
                first_frame_descriptors = []
                for cara in caras:
                    forma = predictor(gray, cara)
                    descriptor = np.array(facial_recognition_model.compute_face_descriptor(frame, forma))
                    first_frame_descriptors.append(descriptor)

                # Comparar los descriptores faciales del primer rostro con los de la base de datos
                for descriptor_actual in first_frame_descriptors:
                    for descriptor_db in descriptors_from_db:
                        distance_value = distance.euclidean(descriptor_actual, descriptor_db)
                        if distance_value < umbral:
                            last_result = "¡Estudiante registrado!"
                            break
                    if last_result is not None:
                        break
                # Si no se encontró ninguna coincidencia, establecer last_result en un valor que indique que el estudiante no está registrado
                if last_result is None:
                    last_result = "¡Estudiante no registrado!"

        # Dibujar un rectángulo alrededor de las caras detectadas
        for cara in caras:
            x, y, w, h = cara.left(), cara.top(), cara.width(), cara.height() 
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # Mostrar el resultado de la comparación en el frame 
        cv2.putText(frame, last_result, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Codificar el frame como JPEG para la transmisión 
        (flag, encodedImage) = cv2.imencode(".jpg", frame) 
        if not flag:
            continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

# Asegúrate de que esta parte esté dentro de la función process_video
if cap is not None:
    cap.release()

# Función para liberar la cámara al cerrar la aplicación de Flask
def liberar_camara_teardown(exception=None):
    if cap is not None:
        cap.release()

# Registrar la función para el evento teardown_appcontext
app.teardown_appcontext(liberar_camara_teardown)