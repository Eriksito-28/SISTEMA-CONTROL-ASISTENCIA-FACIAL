from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Trabajador
from .serializers import (
    TrabajadorSerializer,
    TrabajadorCrearSerializer,
    TrabajadorActualizarSerializer
)
from apps.usuarios.models import Usuario, Rol
from apps.auditoria.services import registrar_auditoria
from django.contrib.auth.hashers import make_password
from apps.usuarios.permissions import EsAdmin
import os
from django.conf import settings




class TrabajadorListarCrearView(APIView):
    permission_classes = [EsAdmin]

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

        # Crear usuario automáticamente al crear trabajador
        try:
            rol = Rol.objects.get(nombre='TRABAJADOR')
            Usuario.objects.create(
                username=trabajador.dni,
                password=make_password('municipalidad2026'),
                trabajador=trabajador,
                rol=rol,
                debe_cambiar_password=True
            )
        except Rol.DoesNotExist:
            pass
        except Exception as e:
            print(f'Error creando usuario automático: {e}')

        registrar_auditoria(
            usuario=request.user,
            accion='CREAR_TRABAJADOR',
            descripcion=f'Trabajador creado: {trabajador.nombres} {trabajador.apellido_paterno} DNI: {trabajador.dni}',
            ip=request.META.get('REMOTE_ADDR', '0.0.0.0')
        )

        return Response(
            TrabajadorSerializer(trabajador).data,
            status=status.HTTP_201_CREATED
        )


class TrabajadorDetalleView(APIView):
    permission_classes = [EsAdmin]

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

    def delete(self, request, pk):
        trabajador = self.get_object(pk)
        if not trabajador:
            return Response(
                {'error': 'Trabajador no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verificar si tiene marcaciones registradas
        if trabajador.marcaciones.exists():
            return Response(
                {'error': 'No se puede eliminar un trabajador con marcaciones registradas. Desactívelo en su lugar.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        nombre_completo = f'{trabajador.nombres} {trabajador.apellido_paterno}'
        dni = trabajador.dni

        # Eliminar usuario asociado primero
        try:
            usuario = Usuario.objects.get(trabajador=trabajador)
            usuario.delete()
        except Usuario.DoesNotExist:
            pass

        trabajador.delete()

        registrar_auditoria(
            usuario=request.user,
            accion='ELIMINAR_TRABAJADOR',
            descripcion=f'Trabajador eliminado: {nombre_completo} DNI: {dni}',
            ip=request.META.get('REMOTE_ADDR', '0.0.0.0')
        )

        return Response(
            {'mensaje': f'Trabajador {nombre_completo} eliminado correctamente'},
            status=status.HTTP_200_OK
        )


class ActivarDesactivarTrabajadorView(APIView):
    permission_classes = [EsAdmin]

    def patch(self, request, pk):
        try:
            trabajador = Trabajador.objects.get(pk=pk)
        except Trabajador.DoesNotExist:
            return Response(
                {'error': 'Trabajador no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        trabajador.activo = not trabajador.activo
        trabajador.save()

        estado = 'activado' if trabajador.activo else 'desactivado'

        registrar_auditoria(
            usuario=request.user,
            accion='ACTIVAR_DESACTIVAR_TRABAJADOR',
            descripcion=f'Trabajador {trabajador.nombres} {trabajador.apellido_paterno} {estado}',
            ip=request.META.get('REMOTE_ADDR', '0.0.0.0')
        )

        return Response(
            {
                'mensaje': f'Trabajador {estado} correctamente',
                'activo': trabajador.activo
            },
            status=status.HTTP_200_OK
        )
    
#para mi foto de la base de datos
class SubirFotoTrabajadorView(APIView):
    permission_classes = [EsAdmin]

    def post(self, request, pk):
        try:
            trabajador = Trabajador.objects.get(pk=pk)
        except Trabajador.DoesNotExist:
            return Response(
                {'error': 'Trabajador no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        imagen_base64 = request.data.get('imagen')
        if not imagen_base64:
            return Response(
                {'error': 'imagen es requerida'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            import base64
            if ',' in imagen_base64:
                imagen_base64 = imagen_base64.split(',')[1]

            imagen_base64 = imagen_base64.strip()
            padding = 4 - len(imagen_base64) % 4
            if padding != 4:
                imagen_base64 += '=' * padding

            imagen_bytes = base64.b64decode(imagen_base64)

            carpeta = os.path.join(settings.MEDIA_ROOT, 'trabajadores')
            os.makedirs(carpeta, exist_ok=True)

            nombre_archivo = f'{trabajador.dni}.jpg'
            ruta_archivo = os.path.join(carpeta, nombre_archivo)

            with open(ruta_archivo, 'wb') as f:
                f.write(imagen_bytes)

            trabajador.foto_url = f'/media/trabajadores/{nombre_archivo}'
            trabajador.save()

            return Response({
                'mensaje': 'Foto actualizada correctamente',
                'foto_url': trabajador.foto_url
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Error al guardar la foto: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )