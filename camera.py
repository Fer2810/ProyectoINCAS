#PRIMER ERROR SOLUCIONADO, AHORA FALTA CORREGIR EL BAJO RENDIMIENTO DE LA CAPTURA DE FRAMES

import cv2
import dlib
import numpy as np
import mysql.connector
from flask import Flask, Response
from scipy.spatial import distance
import pickle

app = Flask(__name__)

# Función para crear la conexión a la base de datos
def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="app_incas"
    ) 

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
umbral = 0.6

def start_camera():
    global cap, camera_running
    if not camera_running:
        cap = cv2.VideoCapture(0)
        camera_running = True

def stop_camera():
    global cap, camera_running
    if camera_running:
        cap.release()
        camera_running = False

def generate():
    global cap
    while camera_running:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Error al capturar el frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        caras = detector(gray)
        
        for cara in caras:
            x, y, w, h = cara.left(), cara.top(), cara.width(), cara.height()
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            forma = predictor(gray, cara)
            descriptor_actual = np.array(facial_recognition_model.compute_face_descriptor(frame, forma))

            for descriptor_db in descriptors_from_db:
                distance_value = distance.euclidean(descriptor_actual, descriptor_db)
                if distance_value < umbral:
                    last_result = "¡Rostro reconocido!"
                    break
                else:
                    last_result = "¡Rostro no reconocido!"

            cv2.putText(frame, last_result, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        (flag, encodedImage) = cv2.imencode(".jpg", frame)
        if not flag:
            continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')


# Asegúrate de que esta parte esté dentro de la función generate
if cap is not None:
    cap.release()

# Función para liberar la cámara al cerrar la aplicación de Flask
def liberar_camara_teardown(exception=None):
    if cap is not None:
        cap.release()

# Registrar la función para el evento teardown_appcontext
app.teardown_appcontext(liberar_camara_teardown)
