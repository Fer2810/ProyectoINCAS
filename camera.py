"""  
Deteccion, extraccion de descriptores faciales, consulta en la base de datos y comparacion en vivo 

##################################################################################################

1. Problemas con el video en vivo, al ser la comparacion en vivo, el video es muy  lento al hacer la consulta y comparacion 
   en cada iteracion del bucle

"""


import cv2
import dlib
import numpy as np
import mysql.connector
from flask import Flask, Response
from scipy.spatial import distance
import pickle
import threading
from conexióndb import get_facial_descriptors_and_names_from_db

app = Flask(__name__)

# Cargar el modelo de predicción facial de dlib
predictor = dlib.shape_predictor("env/Lib/site-packages/dlib/models/shape_predictor_68_face_landmarks.dat")
facial_recognition_model = dlib.face_recognition_model_v1("env/Lib/site-packages/dlib/models/dlib_face_recognition_resnet_model_v1.dat")

# Inicializar el detector de caras de dlib
detector = dlib.get_frontal_face_detector()
cap = None
camera_running = False
last_result = None
names_descriptors_from_db = None

# Función para iniciar la cámara
def start_camera():
    global cap, camera_running, last_result, names_descriptors_from_db
    if not camera_running:
        last_result = None  # Reiniciar last_result al iniciar la cámara
        # Variable para almacenar los nombres y descriptores faciales de la base de datos
        names_descriptors_from_db = get_facial_descriptors_and_names_from_db()
        cap = cv2.VideoCapture(0)
        camera_running = True

# Función para procesar el video
def generate():
    global last_result, names_descriptors_from_db
    while camera_running:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Error al capturar el frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        caras = detector(gray)

        # Verificar si es el primer rostro detectado y compararlo con los descriptores de la base de datos
        if len(caras) > 0:
            for cara in caras:
                forma = predictor(gray, cara)
                descriptor_actual = np.array(facial_recognition_model.compute_face_descriptor(frame, forma))
                for name, descriptor_db in names_descriptors_from_db:
                    distance_value = distance.euclidean(descriptor_actual, descriptor_db)
                    umbral = 0.5
                    if distance_value < umbral:
                        last_result = f"MATCH: {name}"
                        break
                if last_result is not None:
                    break 
            # Si no se encontró ninguna coincidencia, establecer last_result en un valor que indique que el estudiante no está registrado
            if last_result is None:
                last_result = "Estudiante no registrado"
        
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

# Función para detener la cámara
def stop_camera():
    global cap, camera_running, last_result, names_descriptors_from_db
    if camera_running:
        cap.release()
        camera_running = False
        last_result = None 
        names_descriptors_from_db = get_facial_descriptors_and_names_from_db()
        if names_descriptors_from_db:
            names_descriptors_from_db = None

# Asegúrate de que esta parte esté dentro de la función process_video
if cap is not None:
    cap.release()

# Función para liberar la cámara al cerrar la aplicación de Flask
def liberar_camara_teardown(exception=None):
    if cap is not None:
        cap.release()

# Registrar la función para el evento teardown_appcontext
app.teardown_appcontext(liberar_camara_teardown)
