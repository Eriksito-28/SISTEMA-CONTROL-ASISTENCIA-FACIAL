from django.db import models

class ConfiguracionSistema(models.Model):
    hora_inicio_entrada = models.TimeField()
    hora_fin_entrada = models.TimeField()
    hora_inicio_salida = models.TimeField()
    hora_fin_salida = models.TimeField()
    max_intentos = models.IntegerField(default=5)
    max_intentos_faciales = models.IntegerField(default=5)
    umbral_similitud = models.FloatField(default=0.6)
    # IPs autorizadas separadas por coma. Ej: 127.0.0.1, 192.168.1.1
    ip_autorizada = models.TextField(null=True, blank=True)
    control_ip_activo = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'configuracion_sistema'
        verbose_name = 'Configuración del sistema'
        verbose_name_plural = 'Configuraciones del sistema'

    def __str__(self):
        return f'Configuración #{self.id}'

    # Método helper para obtener lista de IPs autorizadas
    def get_ips_autorizadas(self):
        if not self.ip_autorizada:
            return []
        return [ip.strip() for ip in self.ip_autorizada.split(',') if ip.strip()]