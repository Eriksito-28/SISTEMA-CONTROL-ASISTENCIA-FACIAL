"""
Configuración del panel de administración para el modelo auditoría,
permite visualizar y gestionar los registros de auditoría del sistema
"""


from django.contrib import admin
from .models import Auditoria

#columnas que se mostrarán en la lista del panel del administrador
#campos habilitados para búsqueda y filtros en el panel del administrador
@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'usuario',
        'accion',
        'fecha',
        'ip'
    ]
    search_fields = ['usuario__username', 'accion']
    list_filter = ['accion']