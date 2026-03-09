from django.contrib import admin
from .models import Trabajador

# Register your models here.

@admin.register(Trabajador)
class TrabajadorAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'nombres',
        'apellido_paterno',
        'apellido_materno',
        'dni',
        'cargo',
        'activo'
    ]
    search_fields = ['dni', 'nombres', 'apellido_paterno']
    list_filter = ['activo', 'cargo']