from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ConfiguracionSistema
from .serializers import ConfiguracionSistemaSerializer
from apps.auditoria.services import registrar_auditoria
from apps.usuarios.permissions import EsAdmin



class ConfiguracionView(APIView):
    permission_classes = [EsAdmin]

    def get(self, request):
        config = ConfiguracionSistema.objects.first()
        if not config:
            return Response(
                {'error': 'No hay configuración registrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ConfiguracionSistemaSerializer(config)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        config = ConfiguracionSistema.objects.first()
        if not config:
            return Response(
                {'error': 'No hay configuración registrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ConfiguracionSistemaSerializer(
            config,
            data=request.data,
            partial=True
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        try:
            registrar_auditoria(
                usuario=request.user,
                accion='CAMBIO_CONFIGURACION',
                descripcion=f'Se modificó la configuración del sistema: {request.data}',
                ip=request.META.get('REMOTE_ADDR', '0.0.0.0')
            )
        except Exception:
            pass

        return Response(serializer.data, status=status.HTTP_200_OK)