"""
Este módulo define la configuracion de app auditoria,
este registra y gestiona la aplicacion dentro del proyecto
"""

from django.apps import AppConfig

#Tipo de campo automatico usado como clave primario en los modelos
class AuditoriaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.auditoria'
