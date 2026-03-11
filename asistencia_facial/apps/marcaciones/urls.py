from django.urls import path
from .views import (
    MarcacionRegistrarView,
    MarcacionHistorialView,
    MarcacionListarView,
    MarcacionHoyView
)

urlpatterns = [
    path('', MarcacionListarView.as_view(), name='marcacion-listar'),
    path('registrar/', MarcacionRegistrarView.as_view(), name='marcacion-registrar'),
    path('historial/<int:trabajador_id>/', MarcacionHistorialView.as_view(), name='marcacion-historial'),
    path('hoy/', MarcacionHoyView.as_view(), name='marcacion-hoy'),
]