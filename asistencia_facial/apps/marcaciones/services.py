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
    hoy = timezone.localdate()

    # Buscar marcaciones de HOY en hora local (Lima)
    marcaciones_hoy = Marcacion.objects.filter(
        trabajador=trabajador,
        fecha__date=hoy,
        exitoso=True
    ).order_by('fecha')

    # Si no encuentra, buscar con conversión explícita
    if not marcaciones_hoy.exists():
        from django.db.models import F
        ahora_local = timezone.localtime(timezone.now())
        inicio_dia = ahora_local.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_dia = ahora_local.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        marcaciones_hoy = Marcacion.objects.filter(
            trabajador=trabajador,
            fecha__gte=inicio_dia,
            fecha__lte=fin_dia,
            exitoso=True
        ).order_by('fecha')

    entrada_hoy = marcaciones_hoy.filter(tipo='ENTRADA').first()
    salida_hoy = marcaciones_hoy.filter(tipo='SALIDA').first()

    if entrada_hoy and salida_hoy:
        return None, 'Ya registró su entrada y salida de hoy'

    if entrada_hoy and not salida_hoy:
        return 'SALIDA', None

    if not entrada_hoy:
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