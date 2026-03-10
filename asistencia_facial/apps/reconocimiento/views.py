from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from apps.trabajadores.models import Trabajador
from apps.marcaciones.services import registrar_marcacion
from apps.configuracion.models import ConfiguracionSistema
from apps.usuarios.models import Usuario
from .services import generar_embedding, generar_embedding_promedio, comparar_embeddings


# Recibe una o varias imágenes del trabajador desde el panel admin, genera un embedding
# promedio con InsightFace y lo guarda en la base de datos.
# Si se envía una sola imagen usa generar_embedding.
# Si se envían varias imágenes usa generar_embedding_promedio para mayor precisión.
class RegistrarEmbeddingView(APIView):

    def post(self, request):
        trabajador_id = request.data.get('trabajador_id')
        imagen_base64 = request.data.get('imagen')          # Una sola imagen
        imagenes_base64 = request.data.get('imagenes')      # Lista de imágenes

        if not trabajador_id:
            return Response(
                {'error': 'trabajador_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not imagen_base64 and not imagenes_base64:
            return Response(
                {'error': 'Se requiere imagen o imagenes'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            trabajador = Trabajador.objects.get(pk=trabajador_id)
        except Trabajador.DoesNotExist:
            return Response(
                {'error': 'Trabajador no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Si se enviaron múltiples imágenes usar embedding promedio
        if imagenes_base64:
            if not isinstance(imagenes_base64, list):
                return Response(
                    {'error': 'imagenes debe ser una lista'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            embedding, error = generar_embedding_promedio(imagenes_base64)
            metodo = 'promedio'
        else:
            # Una sola imagen
            embedding, error = generar_embedding(imagen_base64)
            metodo = 'simple'

        if error:
            return Response(
                {'error': error},
                status=status.HTTP_400_BAD_REQUEST
            )

        trabajador.embedding = embedding
        trabajador.embedding_actualizado = timezone.now()
        trabajador.save()

        return Response(
            {
                'mensaje': 'Embedding registrado correctamente',
                'metodo': metodo,
                'imagenes_procesadas': len(imagenes_base64) if imagenes_base64 else 1
            },
            status=status.HTTP_200_OK
        )


# Valida que el trabajador exista y esté activo, verifica que tenga embedding registrado,
# genera el embedding de la imagen capturada, compara ambos embeddings y si coinciden
# registra la marcación automáticamente.
class VerificarRostroView(APIView):

    def post(self, request):
        trabajador_id = request.data.get('trabajador_id')
        imagen_base64 = request.data.get('imagen')
        dispositivo = request.data.get('dispositivo', 'No especificado')

        if not trabajador_id or not imagen_base64:
            return Response(
                {'error': 'trabajador_id e imagen son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            trabajador = Trabajador.objects.get(pk=trabajador_id)
        except Trabajador.DoesNotExist:
            return Response(
                {'error': 'Trabajador no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not trabajador.activo:
            return Response(
                {'error': 'Trabajador inactivo'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not trabajador.embedding:
            return Response(
                {'error': 'El trabajador no tiene embedding registrado'},
                status=status.HTTP_400_BAD_REQUEST
            )

        config = ConfiguracionSistema.objects.first()
        if not config:
            return Response(
                {'error': 'No hay configuración del sistema registrada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener usuario para control de intentos faciales
        try:
            usuario = Usuario.objects.get(trabajador=trabajador)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        if usuario.bloqueado:
            return Response(
                {'error': 'Usuario bloqueado. Contacte al administrador'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Generar embedding de la imagen capturada
        embedding_capturado, error = generar_embedding(imagen_base64)
        if error:
            return Response(
                {'error': error},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Comparar embeddings
        verificado, similitud = comparar_embeddings(
            embedding_capturado,
            trabajador.embedding,
            config.umbral_similitud
        )

        if not verificado:
            usuario.intentos_fallidos += 1
            if usuario.intentos_fallidos >= config.max_intentos_faciales:
                usuario.bloqueado = True
                usuario.save()
                return Response(
                    {'error': 'Usuario bloqueado por intentos faciales fallidos'},
                    status=status.HTTP_403_FORBIDDEN
                )
            usuario.save()
            restantes = config.max_intentos_faciales - usuario.intentos_fallidos
            return Response({
                'error': f'Rostro no verificado. Intentos restantes: {restantes}',
                'similitud': similitud
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Verificación exitosa, resetear intentos y registrar marcación
        usuario.intentos_fallidos = 0
        usuario.save()

        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        marcacion, error = registrar_marcacion(trabajador, ip, dispositivo)
        if error:
            return Response(
                {'error': error},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'mensaje': 'Verificación exitosa',
            'similitud': similitud,
            'marcacion': {
                'id': marcacion.id,
                'tipo': marcacion.tipo,
                'estado': marcacion.estado,
                'fecha': marcacion.fecha,
            }
        }, status=status.HTTP_200_OK)