from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer
from .services import validar_login
from .models import Usuario, Rol
from apps.trabajadores.models import Trabajador
from apps.auditoria.services import registrar_auditoria
from django.contrib.auth.hashers import make_password
from apps.usuarios.permissions import EsAdmin


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
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')

        usuario, error = validar_login(username, password)
        if error:
            # Registrar intento fallido en auditoría
            try:
                u = Usuario.objects.get(username=username)
                registrar_auditoria(
                    usuario=u,
                    accion='LOGIN_FALLIDO',
                    descripcion=f'Intento de login fallido: {error}',
                    ip=ip
                )
            except Usuario.DoesNotExist:
                pass
            return Response(
                {'error': error},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Registrar login exitoso en auditoría
        registrar_auditoria(
            usuario=usuario,
            accion='LOGIN_EXITOSO',
            descripcion=f'Inicio de sesión exitoso',
            ip=ip
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

            # Registrar logout en auditoría
            try:
                registrar_auditoria(
                    usuario=request.user,
                    accion='LOGOUT',
                    descripcion='Cierre de sesión',
                    ip=request.META.get('REMOTE_ADDR', '0.0.0.0')
                )
            except Exception:
                pass

            return Response(
                {'mensaje': 'Sesión cerrada correctamente'},
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {'error': 'Token inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )


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
            registrar_auditoria(
                usuario=usuario,
                accion='CAMBIO_PASSWORD_FALLIDO',
                descripcion='Intento de cambio de contraseña fallido',
                ip=request.META.get('REMOTE_ADDR', '0.0.0.0')
            )
            return Response(
                {'error': 'La contraseña actual es incorrecta'},
                status=status.HTTP_400_BAD_REQUEST
            )

        usuario.password = make_password(password_nueva)
        usuario.debe_cambiar_password = False
        usuario.save()

        registrar_auditoria(
            usuario=usuario,
            accion='CAMBIO_PASSWORD',
            descripcion='Contraseña actualizada correctamente',
            ip=request.META.get('REMOTE_ADDR', '0.0.0.0')
        )

        return Response(
            {'mensaje': 'Contraseña actualizada correctamente'},
            status=status.HTTP_200_OK
        )


class DesbloquearUsuarioView(APIView):
    permission_classes = [EsAdmin]

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

        registrar_auditoria(
            usuario=request.user,
            accion='DESBLOQUEAR_USUARIO',
            descripcion=f'Usuario {usuario.username} desbloqueado',
            ip=request.META.get('REMOTE_ADDR', '0.0.0.0')
        )

        return Response(
            {'mensaje': f'Usuario {usuario.username} desbloqueado correctamente'},
            status=status.HTTP_200_OK
        )


class ResetearIntentosFacialesView(APIView):
    permission_classes = [EsAdmin]

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

        registrar_auditoria(
            usuario=request.user,
            accion='RESETEAR_INTENTOS_FACIALES',
            descripcion=f'Intentos faciales reseteados para {usuario.username}',
            ip=request.META.get('REMOTE_ADDR', '0.0.0.0')
        )

        return Response(
            {'mensaje': f'Intentos faciales reseteados para {usuario.username}'},
            status=status.HTTP_200_OK
        )
    
class ListarUsuariosView(APIView):
    permission_classes = [EsAdmin]

    def get(self, request):
        usuarios = Usuario.objects.select_related(
            'trabajador', 'rol'
        ).all().order_by('trabajador__apellido_paterno')

        data = []
        for u in usuarios:
            data.append({
                'id': u.id,
                'username': u.username,
                'rol': u.rol.nombre,
                'nombre_completo': f'{u.trabajador.nombres} {u.trabajador.apellido_paterno} {u.trabajador.apellido_materno}',
                'dni': u.trabajador.dni,
                'cargo': u.trabajador.cargo,
                'activo': u.trabajador.activo,
                'bloqueado': u.bloqueado,
                'intentos_fallidos': u.intentos_fallidos,
                'debe_cambiar_password': u.debe_cambiar_password,
                'ultimo_login': u.ultimo_login,
            })

        return Response({
            'total': len(data),
            'usuarios': data
        }, status=status.HTTP_200_OK)
    
#para el usuario actual
class PerfilView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = request.user
        return Response({
            'id': usuario.id,
            'username': usuario.username,
            'rol': usuario.rol.nombre,
            'nombre_completo': f'{usuario.trabajador.nombres} {usuario.trabajador.apellido_paterno} {usuario.trabajador.apellido_materno}',
            'dni': usuario.trabajador.dni,
            'cargo': usuario.trabajador.cargo,
            'trabajador_id': usuario.trabajador.id,
            'foto_url': usuario.trabajador.foto_url,
            'debe_cambiar_password': usuario.debe_cambiar_password,
            'bloqueado': usuario.bloqueado,
        }, status=status.HTTP_200_OK)