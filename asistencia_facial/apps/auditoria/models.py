"""
Este modelo registra las acciones realizadas por los usuarios, 
la accion, descripcion, fecha y la IP para saber desde donde se hizo
"""

from django.db import models
from apps.usuarios.models import Usuario

#se crea la clase auditoria que representa un registro de auditoria dentro del sistema
class Auditoria(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='auditorias'
    )
    accion = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        db_table = 'auditoria'
        verbose_name = 'Auditoria'
        verbose_name_plural = 'Auditorias'
        ordering = ['-fecha']
    def __str__(self):
        return f'{self.usuario} - {self.accion} - {self.fecha}'