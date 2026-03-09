from django.db import models


class Trabajador(models.Model):
    nombres = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    dni = models.CharField(max_length=8, unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    foto_url = models.CharField(max_length=255, blank=True, null=True)
    embedding = models.JSONField(blank=True, null=True)
    embedding_actualizado = models.DateTimeField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_inicio_laboral = models.DateField()
    fecha_fin_laboral = models.DateField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'trabajadores'
        verbose_name = 'Trabajador'
        verbose_name_plural = 'Trabajadores'

    def __str__(self):
        return f'{self.nombres} {self.apellido_paterno} {self.apellido_materno}'