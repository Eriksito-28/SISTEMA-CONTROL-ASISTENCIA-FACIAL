"""
Este módulo define la configuracion de app configuracion,
este registra y gestiona la aplicacion dentro del proyecto
"""

from django.apps import AppConfig

class ConfiguracionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.configuracion'
