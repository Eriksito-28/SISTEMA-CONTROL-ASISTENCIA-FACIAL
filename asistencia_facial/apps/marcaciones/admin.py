from django.contrib import admin
from .models import Marcacion

# Register your models here.

@admin.register(Marcacion)
class MarcacionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'trabajador',
        'fecha',
        'tipo',
        'estado',
        'exitoso'
    ]
    search_fields = ['trabajador__dni', 'trabajador__nombres']
    list_filter = ['tipo', 'estado', 'exitoso']