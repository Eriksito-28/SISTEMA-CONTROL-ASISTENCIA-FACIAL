from django.utils import timezone
from .models import Marcacion
from apps.configuracion.models import ConfiguracionSistema


def obtener_configuracion():
    config = ConfiguracionSistema.objects.first()
    if not config:
        raise Exception('No hay configuración del sistema registrada')
    return config


def determinar_estado(tipo, hora_actual, config):
    if tipo == 'ENTRADA':
        if hora_actual <= config.hora_fin_entrada:
            return 'PUNTUAL'
        else:
            return 'TARDANZA'
    return None


def validar_marcacion(trabajador):
    ultima_marcacion = Marcacion.objects.filter(
        trabajador=trabajador,
        exitoso=True
    ).order_by('-fecha').first()

    if ultima_marcacion is None:
        return 'ENTRADA', None

    if ultima_marcacion.tipo == 'ENTRADA':
        return 'SALIDA', None

    if ultima_marcacion.tipo == 'SALIDA':
        return 'ENTRADA', None

    return None, 'No se pudo determinar el tipo de marcación'


def registrar_marcacion(trabajador, ip, dispositivo):
    config = obtener_configuracion()
    ahora = timezone.now()
    hora_actual = ahora.time()

    tipo, error = validar_marcacion(trabajador)
    if error:
        return None, error

    estado = determinar_estado(tipo, hora_actual, config)

    marcacion = Marcacion.objects.create(
        trabajador=trabajador,
        fecha=ahora,
        tipo=tipo,
        estado=estado,
        ip=ip,
        dispositivo=dispositivo,
        exitoso=True
    )

    return marcacion, None