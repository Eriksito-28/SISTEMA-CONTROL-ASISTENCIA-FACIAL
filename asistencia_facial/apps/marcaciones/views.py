from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Marcacion
from .serializers import MarcacionSerializer
from .services import registrar_marcacion
from apps.trabajadores.models import Trabajador


class MarcacionRegistrarView(APIView):

    def post(self, request):
        trabajador_id = request.data.get('trabajador_id')
        dispositivo = request.data.get('dispositivo', 'No especificado')

        if not trabajador_id:
            return Response(
                {'error': 'El trabajador_id es requerido'},
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

        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')

        marcacion, error = registrar_marcacion(trabajador, ip, dispositivo)
        if error:
            return Response(
                {'error': error},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = MarcacionSerializer(marcacion)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MarcacionHistorialView(APIView):

    def get(self, request, trabajador_id):
        try:
            trabajador = Trabajador.objects.get(pk=trabajador_id)
        except Trabajador.DoesNotExist:
            return Response(
                {'error': 'Trabajador no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        marcaciones = Marcacion.objects.filter(
            trabajador=trabajador
        ).order_by('-fecha')

        serializer = MarcacionSerializer(marcaciones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MarcacionListarView(APIView):

    def get(self, request):
        marcaciones = Marcacion.objects.all().order_by('-fecha')
        serializer = MarcacionSerializer(marcaciones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)