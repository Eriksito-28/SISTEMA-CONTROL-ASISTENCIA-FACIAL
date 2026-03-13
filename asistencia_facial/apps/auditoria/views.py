"""
Vistas de la API de auditoria 
Permite consultar los registros de auditoria, se crea una clase para listar la 
auditoria en general y otra clase para mostrar un usuario específico
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Auditoria
from .serializers import AuditoriaSerializer
from apps.usuarios.permissions import EsAdmin



#esta clase lista todos los registros de auditoria de manera ordenada
class AuditoriaListarView(APIView):
    permission_classes = [EsAdmin]

    def get(self, request):
        auditorias = Auditoria.objects.all().order_by('-fecha')
        serializer = AuditoriaSerializer(auditorias, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#lo mismo que la clase anterior, pero esta lo hace de un usuario específico 
class AuditoriaUsuarioView(APIView):
    permission_classes = [EsAdmin]

    def get(self, request, usuario_id):
        auditorias = Auditoria.objects.filter(
            usuario_id=usuario_id
        ).order_by('-fecha')
        serializer = AuditoriaSerializer(auditorias, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)