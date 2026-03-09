import numpy as np
import cv2
import base64
from insightface.app import FaceAnalysis


# Inicializar InsightFace una sola vez cuando arranca el servidor
#estoy usando el modelo buffalo_l porque es el más preciso para reconocimiento facial
#se inicializa una sola vez para no cargar el modelo en cada peticion, lo que mejora el rendimiento
#en providers se especifica que se usara la cpu para procesar  
#en face_app.prepare se especifica el tamaño de la imagen 
face_app = FaceAnalysis(
    name='buffalo_l',
    providers=['CPUExecutionProvider']
)
face_app.prepare(ctx_id=0, det_size=(640, 640))


#el frontend enviará la imagen en formato base64, que es texto. Esta función convierte
#ese texto en una imagen que OpenCV puede procesar
#split elimina el prefijo data:image/jpeg;base64 que los navegadores agregan automaticamente 

def decodificar_imagen(imagen_base64):
    try:
        if ',' in imagen_base64:
            imagen_base64 = imagen_base64.split(',')[1]
        
        imagen_base64 = imagen_base64.strip().replace('\n', '').replace('\r', '').replace(' ', '')
        
        # CORREGIR PADDING FALTANTE
        padding = 4 - len(imagen_base64) % 4
        if padding != 4:
            imagen_base64 += '=' * padding
        
        imagen_bytes = base64.b64decode(imagen_base64)
        imagen_array = np.frombuffer(imagen_bytes, dtype=np.uint8)
        imagen = cv2.imdecode(imagen_array, cv2.IMREAD_COLOR)
        
        if imagen is None:
            return None
            
        return imagen
    except Exception as e:
        print(f'Error decodificando imagen: {e}')
        return None


#procesa la imagen con InsightFace y extrae el embedding facial. Valida que haya exactamente
#un rostro en la imagen
#tolist convierte el array de numoy a una lista de python para guardarlo en el campo jsonfield   
def generar_embedding(imagen_base64):
    imagen = decodificar_imagen(imagen_base64)
    if imagen is None:
        return None, 'No se pudo decodificar la imagen'

    faces = face_app.get(imagen)
    if len(faces) == 0:
        return None, 'No se detectó ningún rostro en la imagen'

    if len(faces) > 1:
        return None, 'Se detectó más de un rostro, por favor capture solo un rostro'

    embedding = faces[0].embedding.tolist()
    return embedding, None


#calcula la similitud entre dos embeddings usando similitud coseno. Es la fórmula estándar para comparar
#  vectores de características faciales. Divide el producto punto de los dos vectores entre el producto de
#  sus normas, dando un valor entre -1 y 1 donde 1 significa rostros idénticos.
def comparar_embeddings(embedding1, embedding2, umbral):
    e1 = np.array(embedding1)
    e2 = np.array(embedding2)

    similitud = np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2))

    if similitud >= umbral:
        return True, float(similitud)
    return False, float(similitud)