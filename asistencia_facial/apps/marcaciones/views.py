from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
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


# Devuelve todas las marcaciones del día actual con información
# del trabajador para que el admin pueda ver quién ya marcó hoy.
class MarcacionHoyView(APIView):

    def get(self, request):
        ahora_local = timezone.localtime(timezone.now())
        inicio_dia = ahora_local.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_dia = ahora_local.replace(hour=23, minute=59, second=59, microsecond=999999)

        marcaciones = Marcacion.objects.filter(
            fecha__gte=inicio_dia,
            fecha__lte=fin_dia,
            exitoso=True
        ).order_by('fecha').select_related('trabajador')

        data = []
        for m in marcaciones:
            fecha_local = timezone.localtime(m.fecha)
            data.append({
                'id': m.id,
                'trabajador_id': m.trabajador.id,
                'trabajador_nombre': f'{m.trabajador.nombres} {m.trabajador.apellido_paterno} {m.trabajador.apellido_materno}',
                'dni': m.trabajador.dni,
                'cargo': m.trabajador.cargo,
                'tipo': m.tipo,
                'estado': m.estado,
                'fecha': fecha_local.strftime('%Y-%m-%dT%H:%M:%S%z'),
                'dispositivo': m.dispositivo,
            })

        return Response({
            'fecha': ahora_local.date(),
            'total': len(data),
            'marcaciones': data
        }, status=status.HTTP_200_OK)