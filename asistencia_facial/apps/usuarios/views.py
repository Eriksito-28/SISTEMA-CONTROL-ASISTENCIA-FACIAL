from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer
from .services import validar_login


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