from django.http import JsonResponse
from apps.configuracion.models import ConfiguracionSistema


class ControlIPMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Solo aplicar control en endpoints de reconocimiento y marcaciones
        rutas_protegidas = [
            '/api/reconocimiento/verificar/',
            '/api/marcaciones/registrar/',
        ]

        if request.path in rutas_protegidas:
            try:
                config = ConfiguracionSistema.objects.first()

                if config and config.control_ip_activo:
                    ips_autorizadas = config.get_ips_autorizadas()

                    if ips_autorizadas:
                        ip_cliente = self._obtener_ip(request)

                        if ip_cliente not in ips_autorizadas:
                            return JsonResponse(
                                {
                                    'error': 'Acceso denegado. Su IP no está autorizada para registrar marcaciones',
                                    'ip': ip_cliente
                                },
                                status=403
                            )
            except Exception:
                pass

        response = self.get_response(request)
        return response

    def _obtener_ip(self, request):
        # Obtener IP real considerando proxies
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip