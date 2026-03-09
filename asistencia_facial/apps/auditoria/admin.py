from django.contrib import admin
from .models import Auditoria

# Register your models here.

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