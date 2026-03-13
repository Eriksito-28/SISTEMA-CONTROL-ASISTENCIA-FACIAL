"""
Muestra una lista de campos que se podrán visualizar en el panel del administrador
"""

from django.contrib import admin
from .models import ConfiguracionSistema

#se crea la clase para que se pueda visualizar los siguientes campos
@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'hora_inicio_entrada',
        'hora_fin_entrada',
        'hora_inicio_salida',
        'hora_fin_salida',
        'max_intentos',
        'max_intentos_faciales',
        'umbral_similitud'
        ]