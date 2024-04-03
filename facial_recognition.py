import os
import tempfile
import dlib
import numpy as np

# Cargar el modelo de predicción facial de dlib
predictor = dlib.shape_predictor("ProyectoINCAS/Lib/site-packages/dlib/models/shape_predictor_68_face_landmarks.dat")  # Asegúrate de descargar este modelo
facial_recognition_model = dlib.face_recognition_model_v1("ProyectoINCAS/Lib/site-packages/dlib/models/dlib_face_recognition_resnet_model_v1.dat")  # Asegúrate de descargar este modelo


def extraer_encodings(imagen_bytes):
    try:
        # Crear un archivo temporal para guardar la imagen
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(imagen_bytes)
            temp_file_path = temp_file.name

        # Cargar la imagen desde el archivo temporal
        imagen = dlib.load_rgb_image(temp_file_path)

        # Detectar caras en la imagen
        caras = dlib.get_frontal_face_detector()(imagen)

        # Si se detecta al menos una cara, extraer el encoding
        if caras:
            forma = predictor(imagen, caras[0])
            encoding = np.array(facial_recognition_model.compute_face_descriptor(imagen, forma))
            return encoding
        else:
            print("No se detectaron caras en la imagen.")
            return None
    finally:
        # Eliminar el archivo temporal después de su uso
        os.unlink(temp_file_path)
