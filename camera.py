import cv2
import dlib
import numpy as np
import mysql.connector
from flask import Flask
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
    descriptors_np = []
    for descriptor in descriptors:
        descriptor_np = pickle.loads(descriptor[0])
        descriptors_np.append(descriptor_np)
    
    return descriptors_np

# Cargar el modelo de predicción facial de dlib
predictor = dlib.shape_predictor("env/Lib/site-packages/dlib/models/shape_predictor_68_face_landmarks.dat")
facial_recognition_model = dlib.face_recognition_model_v1("env/Lib/site-packages/dlib/models/dlib_face_recognition_resnet_model_v1.dat")

# Inicializar el detector de caras de dlib
detector = dlib.get_frontal_face_detector()
cap = None
camera_running = False

# Inicializar la cámara (puedes ajustar el índice de la cámara según tu configuración)
def start_camera():
    global descriptores_faciales, cap, camera_running
    if not camera_running:
        cap = cv2.VideoCapture(0)
        descriptores_faciales = None  # Restablecer descriptores_faciales
        camera_running = True

def stop_camera():
    global descriptores_faciales, cap, camera_running
    if camera_running:
        cap.release()
        camera_running = False

# Variable para almacenar los descriptores faciales
# descriptores_faciales = None



def generate():
    global descriptores_faciales, cap, last_result
    # Obtener los descriptores faciales de la base de datos
    descriptors_from_db = get_facial_descriptors_from_db()
    
    # Capturar descriptores faciales
    while camera_running:
        # Leer el frame desde la cámara
        ret, frame = cap.read()

        if not ret or frame is None:
            print("Error al capturar el frame")
            break

        # Convertir a escala de grises para la detección facial
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detectar caras en el frame
        caras = detector(gray)

        # Iterar sobre las caras detectadas
        for cara in caras:
            # Obtener las coordenadas del rectángulo alrededor de la cara
            x, y, w, h = cara.left(), cara.top(), cara.width(), cara.height()

            # Dibujar un rectángulo alrededor de la cara
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Extraer descriptores faciales
            if descriptores_faciales is None:
                forma = predictor(gray, cara)
                descriptores_faciales = np.array(facial_recognition_model.compute_face_descriptor(frame, forma))
                #print(descriptores_faciales)
                
                # Comparar los descriptores faciales utilizando la distancia euclidiana
                for descriptors_np in descriptors_from_db:
                    db_descriptor = descriptors_np
                    distance_value = distance.euclidean(descriptores_faciales.flatten(), db_descriptor.flatten())

                    
                    umbral = 0.7
                    if distance_value < umbral:
                        last_result =  ("¡Descriptores faciales coincidentes!")
                    else:
                        last_result = ("¡Descriptores faciales no coincidentes!")

        # Mostrar el resultado en el frame
        cv2.putText(frame, last_result, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Codificar el frame para enviarlo al navegador
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
