from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Trabajador
from .serializers import (
    TrabajadorSerializer,
    TrabajadorCrearSerializer,
    TrabajadorActualizarSerializer
)


#esta clase realiza dos operaciones, muestra todos los trabajadores y crea uno nuevo 
class TrabajadorListarCrearView(APIView):

    def get(self, request):
        trabajadores = Trabajador.objects.all().order_by('apellido_paterno')
        serializer = TrabajadorSerializer(trabajadores, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TrabajadorCrearSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        trabajador = serializer.save()
        return Response(
            TrabajadorSerializer(trabajador).data,
            status=status.HTTP_201_CREATED
        )


#esta clas maneja muchas más opecaciones que la anterior y 
#la diferencia es que esta lo hace sobre un trabajador específico 
class TrabajadorDetalleView(APIView):


    def get_object(self, pk):
        try:
            return Trabajador.objects.get(pk=pk)
        except Trabajador.DoesNotExist:
            return None

    def get(self, request, pk):
        trabajador = self.get_object(pk)
        if not trabajador:
            return Response(
                {'error': 'Trabajador no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TrabajadorSerializer(trabajador)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        trabajador = self.get_object(pk)
        if not trabajador:
            return Response(
                {'error': 'Trabajador no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TrabajadorActualizarSerializer(
            trabajador,
            data=request.data
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        trabajador = serializer.save()
        return Response(
            TrabajadorSerializer(trabajador).data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        trabajador = self.get_object(pk)
        if not trabajador:
            return Response(
                {'error': 'Trabajador no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TrabajadorActualizarSerializer(
            trabajador,
            data=request.data,
            partial=True
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        trabajador = serializer.save()
        return Response(
            TrabajadorSerializer(trabajador).data,
            status=status.HTTP_200_OK
        )