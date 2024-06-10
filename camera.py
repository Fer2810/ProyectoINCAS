import base64
import cv2
import dlib
import numpy as np
from flask import Flask
from scipy.spatial import distance
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
processing = False  # Bandera para controlar el proceso de reinicio

# Variable para almacenar los nombres y descriptores faciales de la base de datos
names_descriptors_from_db = get_facial_descriptors_and_names_from_db()

# Variable para almacenar el resultado de la comparación
last_result = None

# Variable para almacenar los descriptores faciales del primer rostro detectado
descriptor = None

primer_rostro_detectado = None

# Función para iniciar la cámara
def start_camera():
    global cap, camera_running, last_result, names_descriptors_from_db, processing, student_info, descriptor, primer_rostro_detectado
    if not camera_running:
        last_result = None  # Reiniciar last_result al iniciar la cámara
        # Variable para almacenar los nombres y descriptores faciales de la base de datos
        names_descriptors_from_db = None
        cap = cv2.VideoCapture(0)
        camera_running = True
        processing = False  # Reiniciar la bandera de procesamiento
        student_info = None
        descriptor = None
        primer_rostro_detectado = None

# Función para detener la cámara
def stop_camera():
    global cap, camera_running, last_result, descriptor, student_info,names_descriptors_from_db, primer_rostro_detectado
    if camera_running:
        cap.release()
        camera_running = False
        last_result = None
        descriptor = None
        student_info = None
        names_descriptors_from_db = None
        primer_rostro_detectado = None

# Función para reiniciar los valores después de 5 segundos
def reset_values():
    global last_result, descriptor, processing, student_info, student_info,names_descriptors_from_db, primer_rostro_detectado
    last_result = None
    descriptor = None
    processing = False  # Reiniciar la bandera de procesamiento
    student_info = None
    names_descriptors_from_db = None
    primer_rostro_detectado = None


# Función para procesar el video
def generate():
    global descriptor, last_result, processing, student_info, names_descriptors_from_db, primer_rostro_detectado
    
    
    while camera_running:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Error al capturar el frame")
            break
        
        try:
             ret, frame = cap.read()
        except cv2.error as e:
             print(f"Error de OpenCV: {e}")
             continue  # O realiza alguna otra acción de manejo de errores

    

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        caras = detector(gray)

        # Verificar si se ha reiniciado la cámara
        if not last_result:
            descriptor = None

        # Actualizar los descriptores faciales y nombres de la base de datos en cada iteración
        if not processing:
            names_descriptors_from_db = get_facial_descriptors_and_names_from_db()

        # Verificar si es el primer rostro detectado y compararlo con los descriptores de la base de datos
        if descriptor is None and not primer_rostro_detectado:
            if len(caras) > 0:
                # Marcar que se ha detectado el primer rostro
                primer_rostro_detectado = True
                # Extraer descriptores faciales del primer rostro detectado
                for cara in caras:
                    forma = predictor(gray, cara)
                    descriptor = np.array(facial_recognition_model.compute_face_descriptor(frame, forma))
                    break

       # Si se ha detectado el primer rostro y hay caras detectadas, proceder con la comparación de descriptores faciales
        if primer_rostro_detectado and len(caras) > 0:
            for descriptor_actual in [descriptor]:
                for nie, name, bachillerato, descriptor_db, imagen_blob in names_descriptors_from_db:
                    distance_value = distance.euclidean(descriptor_actual, descriptor_db)
                    umbral = 0.5
                    if distance_value < umbral:
                        last_result = f"MATCH: {name}"
                        imagen_base64 = base64.b64encode(imagen_blob).decode('utf-8')
                        student_info = f"{nie},{name},{bachillerato},{imagen_base64}"
                        break
                if last_result is not None:
                    break

        # Si no se encontró ninguna coincidencia y se detectó el primer rostro, establecer last_result en un valor que indique que el estudiante no está registrado
        if last_result is None and primer_rostro_detectado:
            last_result = "Estudiante no registrado"

        # Función para reiniciar los valores después de 5 segundos
        if not processing:
            threading.Timer(3, reset_values).start()
            processing = True  # Establecer la bandera de procesamiento

        # Dibujar un rectángulo alrededor de las caras detectadas y mostrar el resultado en el frame
        # Dibujar un rectángulo alrededor de las caras detectadas y mostrar el resultado en el frame
        for cara in caras:
            x, y, w, h = cara.left(), cara.top(), cara.width(), cara.height()

            # Calcular las coordenadas para centrar el rectángulo en la pantalla
            centro_x = x + w // 2
            centro_y = y + h // 2
            ancho_recuadro = 200  # Ancho del recuadro de detección facial
            alto_recuadro = 200   # Alto del recuadro de detección facial
            x = centro_x - ancho_recuadro // 2
            y = centro_y - alto_recuadro // 2

            # Limitar las coordenadas para asegurarse de que el rectángulo esté dentro de los límites de la pantalla
            x = max(0, x)
            y = max(0, y)
            x = min(frame.shape[1] - ancho_recuadro, x)
            y = min(frame.shape[0] - alto_recuadro, y)

            # Dibujar el rectángulo centrado
            cv2.rectangle(frame, (x, y), (x+ancho_recuadro, y+alto_recuadro), (255, 0, 0), 2)

        # Añadir el texto al frame
        if last_result is not None:
            cv2.putText(frame, last_result, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

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

  