"""
Estas son las rutas para la API de auditoria

Define los endpoints para consultar los registros de auditoria del sistema, 
incluye un listado general y uno especifico por cada usuario
"""

from django.urls import path
from .views import AuditoriaListarView, AuditoriaUsuarioView

#el primer pathlista todos los registros de auditoría 
#el segundo muestra de un usuario específico 
urlpatterns = [
    path('', AuditoriaListarView.as_view(), name='auditoria-listar'),
    path('<int:usuario_id>/', AuditoriaUsuarioView.as_view(), name='auditoria-usuario'),
]