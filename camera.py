
""" 
$ Deteccion, extración y comparacion en tiempo real de descriptores faciales.
$ Video frame fluido
$ Actualizacion de la base de datos al momento de cerrar la camara


??? Falta reiniciar el script despues de cierto intervalo de tiempo cuando se muestre un resultado 
??? Falta mostrar los datos del alumno en la pantalla estilo carnet de estudiante
??? Falta registrar la hora de llegada en la tabla 



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
names_descriptors_from_db = None

# Variable para almacenar el resultado de la comparación
last_result = None

# Variable para almacenar los descriptores faciales del primer rostro detectado
first_frame_descriptors = None

# Función para iniciar la cámara
def start_camera():
    global cap, camera_running, last_result, names_descriptors_from_db
    if not camera_running:
        #last_result = "Esperando..."  # Reiniciar last_result al iniciar la cámara
        names_descriptors_from_db = get_facial_descriptors_and_names_from_db()
        cap = cv2.VideoCapture(0)
        camera_running = True

# Función para detener la cámara
def stop_camera():
    global cap, camera_running, last_result, names_descriptors_from_db
    if camera_running:
        cap.release()
        camera_running = False
        last_result = None
        names_descriptors_from_db = None

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

        # Si se detecta al menos una cara, obtener descriptores faciales y comparar con la base de datos
        if len(caras) > 0:
            if first_frame_descriptors is None:
                # Extraer descriptores faciales del primer rostro detectado
                first_frame_descriptors = []
                for cara in caras:
                    forma = predictor(gray, cara)
                    descriptor = np.array(facial_recognition_model.compute_face_descriptor(frame, forma))
                    first_frame_descriptors.append(descriptor)

                # Comparar los descriptores faciales del primer rostro con los de la base de datos
                match_found = False
                for descriptor_actual in first_frame_descriptors:
                    for name, descriptor_db in names_descriptors_from_db:
                        distance_value = distance.euclidean(descriptor_actual, descriptor_db)
                        umbral = 0.5
                        if distance_value < umbral:
                            last_result = f"MATCH: {name}"
                            match_found = True
                            break
                    if match_found:
                        break

                if not match_found:
                    last_result = "No se encontraron coincidencias"

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

