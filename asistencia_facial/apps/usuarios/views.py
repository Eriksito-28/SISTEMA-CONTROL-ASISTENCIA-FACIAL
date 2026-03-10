from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer
from .services import validar_login
from .models import Usuario, Rol
from apps.trabajadores.models import Trabajador
from django.contrib.auth.hashers import make_password


def get_tokens_for_user(usuario):
    refresh = RefreshToken()
    refresh['user_id'] = usuario.id
    refresh['username'] = usuario.username
    refresh['rol'] = usuario.rol.nombre
    refresh['nombre_completo'] = f'{usuario.trabajador.nombres} {usuario.trabajador.apellido_paterno}'

    access = refresh.access_token
    access['user_id'] = usuario.id
    access['username'] = usuario.username
    access['rol'] = usuario.rol.nombre
    access['nombre_completo'] = f'{usuario.trabajador.nombres} {usuario.trabajador.apellido_paterno}'

    return refresh, access


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        usuario, error = validar_login(username, password)
        if error:
            return Response(
                {'error': error},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh, access = get_tokens_for_user(usuario)

        return Response({
            'access': str(access),
            'refresh': str(refresh),
            'debe_cambiar_password': usuario.debe_cambiar_password,
            'usuario': {
                'id': usuario.id,
                'username': usuario.username,
                'rol': usuario.rol.nombre,
                'nombre_completo': f'{usuario.trabajador.nombres} {usuario.trabajador.apellido_paterno}',
                'trabajador_id': usuario.trabajador.id,
            }
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'mensaje': 'Sesión cerrada correctamente'},
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {'error': 'Token inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )


# Permite al usuario cambiar su contraseña.
# Si debe_cambiar_password=True, después de cambiarla se pone en False.

class CambiarPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        password_actual = request.data.get('password_actual')
        password_nueva = request.data.get('password_nueva')

        if not password_actual or not password_nueva:
            return Response(
                {'error': 'password_actual y password_nueva son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(password_nueva) < 6:
            return Response(
                {'error': 'La nueva contraseña debe tener mínimo 6 caracteres'},
                status=status.HTTP_400_BAD_REQUEST
            )

        usuario = request.user

        if not usuario.check_password(password_actual):
            return Response(
                {'error': 'La contraseña actual es incorrecta'},
                status=status.HTTP_400_BAD_REQUEST
            )

        usuario.password = make_password(password_nueva)
        usuario.debe_cambiar_password = False
        usuario.save()

        return Response(
            {'mensaje': 'Contraseña actualizada correctamente'},
            status=status.HTTP_200_OK
        )

# Desbloquea un usuario bloqueado por intentos fallidos.
class DesbloquearUsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        usuario.bloqueado = False
        usuario.intentos_fallidos = 0
        usuario.save()

        return Response(
            {'mensaje': f'Usuario {usuario.username} desbloqueado correctamente'},
            status=status.HTTP_200_OK
        )


# Resetea los intentos faciales fallidos de un usuario.
class ResetearIntentosFacialesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        usuario.intentos_fallidos = 0
        usuario.bloqueado = False
        usuario.save()

        return Response(
            {'mensaje': f'Intentos faciales reseteados para {usuario.username}'},
            status=status.HTTP_200_OK
        )