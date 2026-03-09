from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ConfiguracionSistema
from .serializers import ConfiguracionSistemaSerializer
from apps.auditoria.services import registrar_auditoria
from apps.usuarios.models import Usuario


#en la linea primera funcion se obtiene el primer y unico registro de configuracion,
#  por eso usamos first en vez de buscarlo por ID
class ConfiguracionView(APIView):

    def get(self, request):
        config = ConfiguracionSistema.objects.first()
        if not config:
            return Response(
                {'error': 'No hay configuración registrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ConfiguracionSistemaSerializer(config)
        return Response(serializer.data, status=status.HTTP_200_OK)

    #en la segunda funcion se puede actualizar los campos enviados
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

        # Registrar en auditoría, obtiene el id de quien hizo el cambio 
        try:
            usuario_id = request.auth.payload.get('user_id')
            usuario = Usuario.objects.get(pk=usuario_id)
            registrar_auditoria(
                usuario=usuario,
                accion='CAMBIO_CONFIGURACION',
                descripcion=f'Se modificó la configuración del sistema: {request.data}',
                ip=request.META.get('REMOTE_ADDR', '0.0.0.0')
            )
        except Exception:
            pass

        return Response(serializer.data, status=status.HTTP_200_OK)