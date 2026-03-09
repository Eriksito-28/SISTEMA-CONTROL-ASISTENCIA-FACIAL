from django.contrib import admin
from .models import Rol, Usuario

# Register your models here.

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'descripcion']
    search_fields = ['nombre']

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'username',
        'rol',
        'bloqueado',
        'intentos_fallidos',
        'ultimo_login'
    ]
    search_fields = ['username']
    list_filter = ['bloqueado', 'rol']