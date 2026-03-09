from django.contrib import admin
from .models import ConfiguracionSistema

# Register your models here.

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