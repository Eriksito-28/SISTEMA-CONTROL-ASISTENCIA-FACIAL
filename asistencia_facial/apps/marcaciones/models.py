from django.db import models
from apps.trabajadores.models import Trabajador


class Marcacion(models.Model):

    # Opciones válidas para el campo tipo
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
    ]

    # Opciones válidas para el campo estado
    ESTADO_CHOICES = [
        ('PUNTUAL', 'Puntual'),
        ('TARDANZA', 'Tardanza'),
    ]

    trabajador = models.ForeignKey(
        Trabajador,
        on_delete=models.PROTECT,
        related_name='marcaciones'
    )
    fecha = models.DateTimeField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        blank=True,
        null=True
    )
    ip = models.CharField(max_length=45, blank=True, null=True)
    dispositivo = models.CharField(max_length=150, blank=True, null=True)
    exitoso = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'marcaciones'
        verbose_name = 'Marcación'
        verbose_name_plural = 'Marcaciones'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.trabajador} - {self.tipo} - {self.fecha}'