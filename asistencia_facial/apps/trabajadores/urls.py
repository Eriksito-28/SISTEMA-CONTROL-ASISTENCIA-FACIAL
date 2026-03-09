from django.urls import path
from .views import TrabajadorListarCrearView, TrabajadorDetalleView


# El primer path vaco pertenece a api/trabajadores 
#El segundo que esta en entre los signos de mayor y 
#menor es para que capture el id del trabajador y lo pase a la vista  
urlpatterns = [
    path('', TrabajadorListarCrearView.as_view(), name='trabajador-listar-crear'),
    path('<int:pk>/', TrabajadorDetalleView.as_view(), name='trabajador-detalle'),
]