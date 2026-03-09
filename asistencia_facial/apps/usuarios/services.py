from django.utils import timezone
from .models import Usuario
from apps.configuracion.models import ConfiguracionSistema


def obtener_configuracion():
    config = ConfiguracionSistema.objects.first()
    if not config:
        raise Exception('No hay configuración del sistema registrada')
    return config


#verifica si el usuario existe 
def validar_login(username, password):
    
    try:
        usuario = Usuario.objects.select_related(
            'trabajador', 'rol'
        ).get(username=username)
    except Usuario.DoesNotExist:
        return None, 'Credenciales incorrectas'

    # Verificar si está bloqueado
    if usuario.bloqueado:
        return None, 'Usuario bloqueado. Contacte al administrador'

    # Verificar si el trabajador está activo
    if not usuario.trabajador.activo:
        return None, 'Trabajador inactivo. Contacte al administrador'

    # Verificar vigencia laboral
    hoy = timezone.now().date()
    if usuario.trabajador.fecha_fin_laboral:
        if hoy > usuario.trabajador.fecha_fin_laboral:
            return None, 'Acceso desactivado por fin de contrato'

    # Verificar contraseña
    config = obtener_configuracion()
    if not usuario.check_password(password):
        usuario.intentos_fallidos += 1
        if usuario.intentos_fallidos >= config.max_intentos:
            usuario.bloqueado = True
            usuario.save()
            return None, 'Usuario bloqueado por intentos fallidos'
        usuario.save()
        restantes = config.max_intentos - usuario.intentos_fallidos
        return None, f'Contraseña incorrecta. Intentos restantes: {restantes}'

    # Login exitoso
    usuario.intentos_fallidos = 0
    usuario.ultimo_login = timezone.now()
    usuario.save()

    return usuario, None