
""" 
$ Deteccion, extración y comparacion en tiempo real de descriptores faciales.
$ Video frame fluido
$ Actualizacion de la base de datos al momento de cerrar la camara



??? Falta mostrar los datos del alumno en la pantalla estilo carnet de estudiante
??? Falta registrar la hora de llegada en la tabla 



"""

import cv2
import dlib
import numpy as np
from flask import Flask
from scipy.spatial import distance
import threading
from conexióndb import get_facial_descriptors_and_names_from_db

app = Flask(__name__)

# Cargar el modelo de predicción facial de dlib
predictor = dlib.shape_predictor("ProyectoINCAS/env/Lib/site-packages/dlib/models/shape_predictor_68_face_landmarks.dat")
facial_recognition_model = dlib.face_recognition_model_v1("ProyectoINCAS/env/Lib/site-packages/dlib/models/dlib_face_recognition_resnet_model_v1.dat")

# Inicializar el detector de caras de dlib
detector = dlib.get_frontal_face_detector()
cap = None
camera_running = False
processing = False  # Bandera para controlar el proceso de reinicio

# Variable para almacenar los nombres y descriptores faciales de la base de datos
names_descriptors_from_db = get_facial_descriptors_and_names_from_db()

# Variable para almacenar el resultado de la comparación
last_result = None

# Variable para almacenar los descriptores faciales del primer rostro detectado
descriptor = None

# Función para iniciar la cámara
def start_camera():
    global cap, camera_running, last_result, names_descriptors_from_db, processing, student_info, descriptor
    if not camera_running:
        last_result = None  # Reiniciar last_result al iniciar la cámara
        # Variable para almacenar los nombres y descriptores faciales de la base de datos
        names_descriptors_from_db = None
        cap = cv2.VideoCapture(0)
        camera_running = True
        processing = False  # Reiniciar la bandera de procesamiento
        student_info = None
        descriptor = None

# Función para detener la cámara
def stop_camera():
    global cap, camera_running, last_result, descriptor, student_info,names_descriptors_from_db
    if camera_running:
        cap.release()
        camera_running = False
        last_result = None
        descriptor = None
        student_info = None
        names_descriptors_from_db = None

# Función para reiniciar los valores después de 5 segundos
def reset_values():
    global last_result, descriptor, processing, student_info, student_info,names_descriptors_from_db
    last_result = None
    descriptor = None
    processing = False  # Reiniciar la bandera de procesamiento
    student_info = None
    names_descriptors_from_db = None

# Función para procesar el video
def generate():
    global descriptor, last_result, processing, student_info, names_descriptors_from_db
    while camera_running:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Error al capturar el frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        caras = detector(gray)
        
        

        # Verificar si se ha reiniciado la cámara
        if not last_result:
            descriptor = None

        # Actualizar los descriptores faciales y nombres de la base de datos en cada iteración
        if not processing:
            names_descriptors_from_db = get_facial_descriptors_and_names_from_db()

        # Verificar si es el primer rostro detectado y compararlo con los descriptores de la base de datos
        if descriptor is None:
            if len(caras) > 0:
                # Extraer descriptores faciales del primer rostro detectado
                first_frame_descriptors = []
                for cara in caras:
                    forma = predictor(gray, cara)
                    descriptor = np.array(facial_recognition_model.compute_face_descriptor(frame, forma))
                    first_frame_descriptors.append(descriptor.copy())  # Corregir el error de append
                    # Utilizamos una copia del descriptor para evitar problemas de referencia
                    break  # Solo necesitamos el primer rostro

                # Comparar los descriptores faciales del primer rostro con los de la base de datos
                for descriptor_actual in first_frame_descriptors:
                    for  nit,  name, bachillerato, descriptor_db in names_descriptors_from_db:
                        distance_value = distance.euclidean(descriptor_actual, descriptor_db)
                        umbral = 0.5
                        if distance_value < umbral:
                            last_result = f"MATCH: {name}"
                            student_info = f" {nit},  {name},  {bachillerato}"
                            break
                        
                    if last_result is not None:
                        break

        # Si no se encontró ninguna coincidencia, establecer last_result en un valor que indique que el estudiante no está registrado
        if last_result is None and first_frame_descriptors:
            last_result = "Estudiante no registrado"

        # Función para reiniciar los valores después de 5 segundos
        if not processing:
            threading.Timer(3, reset_values).start()
            processing = True  # Establecer la bandera de procesamiento

        # Dibujar un rectángulo alrededor de las caras detectadas y mostrar el resultado en el frame
        for cara in caras:
            x, y, w, h = cara.left(), cara.top(), cara.width(), cara.height()
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, last_result, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Codificar el frame como JPEG para la transmisión
        (flag, encodedImage) = cv2.imencode(".jpg", frame)
        if not flag:
            continue
        
        # Enviar el frame codificado a través de SSE
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + bytearray(encodedImage) + b"\r\n"
        
        if student_info is not None:
            yield b"data: " + student_info.encode() + b"\n\n"

# Asegúrate de que esta parte esté dentro de la función process_video
if cap is not None:
    cap.release()

# Función para liberar la cámara al cerrar la aplicación de Flask
def liberar_camara_teardown(exception=None):
    if cap is not None:
        cap.release()

# Registrar la función para el evento teardown_appcontext
app.teardown_appcontext(liberar_camara_teardown)
  




""" 
SOLUCIONES A LA MUESTRA DE DATOS EN EL HTML 


1. Montar los datos dentro de la tarjeta 

2. Mostrar o mover el resuldado dentro  del videoframe hacia afuera del videoframe colocandolo como texto normal a la derecha





"""