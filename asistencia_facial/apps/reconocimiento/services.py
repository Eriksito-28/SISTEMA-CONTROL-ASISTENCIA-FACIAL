import numpy as np
import cv2
import base64
from insightface.app import FaceAnalysis


# Inicializar InsightFace una sola vez cuando arranca el servidor
# Se usa buffalo_l porque es el más preciso para reconocimiento facial
# Se inicializa una sola vez para no cargar el modelo en cada petición
# En providers se especifica que se usará la CPU para procesar
face_app = FaceAnalysis(
    name='buffalo_l',
    providers=['CPUExecutionProvider']
)
face_app.prepare(ctx_id=0, det_size=(640, 640))


# El frontend enviará la imagen en formato base64, que es texto.
# Esta función convierte ese texto en una imagen que OpenCV puede procesar.
# split elimina el prefijo data:image/jpeg;base64 que los navegadores agregan automáticamente.
# Se redimensiona si es muy pequeña y se mejora brillo/contraste automáticamente.
def decodificar_imagen(imagen_base64):
    try:
        if ',' in imagen_base64:
            imagen_base64 = imagen_base64.split(',')[1]
        
        imagen_base64 = imagen_base64.strip().replace('\n', '').replace('\r', '').replace(' ', '')
        
        # Corregir padding faltante
        padding = 4 - len(imagen_base64) % 4      
        if padding != 4:
            imagen_base64 += '=' * padding
        
        imagen_bytes = base64.b64decode(imagen_base64)
        imagen_array = np.frombuffer(imagen_bytes, dtype=np.uint8)
        imagen = cv2.imdecode(imagen_array, cv2.IMREAD_COLOR)
        
        if imagen is None:
            return None

        # Redimensionar si es muy pequeña para mejorar detección
        alto, ancho = imagen.shape[:2]
        if ancho < 640 or alto < 640:
            factor = 640 / min(ancho, alto)
            imagen = cv2.resize(imagen, None, fx=factor, fy=factor,
                                interpolation=cv2.INTER_LINEAR)

        # Mejorar brillo y contraste automáticamente
        imagen = cv2.convertScaleAbs(imagen, alpha=1.2, beta=10)

        return imagen
    except Exception as e:
        print(f'Error decodificando imagen: {e}')
        return None


# Procesa la imagen con InsightFace y extrae el embedding facial.
# Valida que haya exactamente un rostro en la imagen y que tenga buena calidad.
# tolist convierte el array de numpy a una lista de Python para guardarlo en JSONField.
def generar_embedding(imagen_base64):
    imagen = decodificar_imagen(imagen_base64)
    if imagen is None:
        return None, 'No se pudo decodificar la imagen'

    faces = face_app.get(imagen)
    if len(faces) == 0:
        return None, 'No se detectó ningún rostro. Asegúrese de tener buena iluminación y mirar de frente'

    if len(faces) > 1:
        return None, 'Se detectó más de un rostro, por favor capture solo un rostro'

    # Verificar calidad del rostro detectado
    face = faces[0]
    det_score = face.det_score  # Score de confianza de detección (0 a 1)

    if det_score < 0.7:
        return None, f'Rostro detectado con baja calidad ({det_score:.2f}). Mejore la iluminación'

    embedding = face.embedding.tolist()
    return embedding, None


# Recibe una lista de imágenes en base64, genera un embedding por cada una
# y retorna el promedio normalizado. Esto mejora significativamente la precisión
# porque el embedding representa el rostro en diferentes condiciones.
# Se requieren mínimo 2 imágenes y máximo 5.
def generar_embedding_promedio(imagenes_base64):
    if len(imagenes_base64) < 2:
        return None, 'Se requieren mínimo 2 imágenes para generar embedding promedio'

    if len(imagenes_base64) > 5:
        return None, 'Se permiten máximo 5 imágenes'

    embeddings = []

    for i, imagen_base64 in enumerate(imagenes_base64):
        embedding, error = generar_embedding(imagen_base64)
        if error:
            return None, f'Error en imagen {i + 1}: {error}'
        embeddings.append(embedding)

    # Promediar todos los embeddings
    embedding_promedio = np.mean(embeddings, axis=0)

    # Normalizar el embedding promedio (importante para similitud coseno)
    norma = np.linalg.norm(embedding_promedio)
    embedding_normalizado = (embedding_promedio / norma).tolist()

    return embedding_normalizado, None


# Calcula la similitud entre dos embeddings usando similitud coseno.
# Es la fórmula estándar para comparar vectores de características faciales.
# Divide el producto punto de los dos vectores entre el producto de sus normas,
# dando un valor entre -1 y 1 donde 1 significa rostros idénticos.
def comparar_embeddings(embedding1, embedding2, umbral):
    e1 = np.array(embedding1)
    e2 = np.array(embedding2)

    similitud = np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2))

    if similitud >= umbral:
        return True, float(similitud)
    return False, float(similitud)