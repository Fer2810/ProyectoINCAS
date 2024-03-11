import cv2
import dlib
import numpy as np
from flask import Flask

app = Flask(__name__)

# Cargar el modelo de predicción facial de dlib
predictor = dlib.shape_predictor("env/Lib/site-packages/dlib/models/shape_predictor_68_face_landmarks.dat")
facial_recognition_model = dlib.face_recognition_model_v1("env/Lib/site-packages/dlib/models/dlib_face_recognition_resnet_model_v1.dat")

# Inicializar el detector de caras de dlib
detector = dlib.get_frontal_face_detector()

# Inicializar la cámara (puedes ajustar el índice de la cámara según tu configuración)
cap = cv2.VideoCapture(0)

# Variable para almacenar los descriptores faciales
descriptores_faciales = None

def generate():
    global descriptores_faciales
    # Capturar descriptores faciales
    while True:
        # Leer el frame desde la cámara
        ret, frame = cap.read()

        if not ret:
            print("Error al capturar el frame")
            cap.release()  # Asegúrate de cerrar la conexión en caso de error
            continue

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
                print(descriptores_faciales)

        (flag, encodedImage) = cv2.imencode(".jpg", frame)
        if not flag:
            continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

# Función para liberar la cámara al cerrar la aplicación de Flask
def liberar_camara_teardown(exception=None):
    if cap is not None:
        cap.release()

# Registrar la función para el evento teardown_appcontext
app.teardown_appcontext(liberar_camara_teardown)
