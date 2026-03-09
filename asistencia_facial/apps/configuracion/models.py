from django.db import models

# Create your models here.

class ConfiguracionSistema(models.Model):
    hora_inicio_entrada = models.TimeField()
    hora_fin_entrada = models.TimeField()
    hora_inicio_salida = models.TimeField()
    hora_fin_salida = models.TimeField()
    max_intentos = models.IntegerField(default=5)
    max_intentos_faciales = models.IntegerField(default=5)
    umbral_similitud = models.FloatField(default=0.6)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'configuracion_sistema'
        verbose_name = 'Configuración del sistema'
        verbose_name_plural = 'Configuraciones del sistema'
    def __str__(self):
        return f'Configuración #{self.id}'