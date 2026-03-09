from django.urls import path
from .views import RegistrarEmbeddingView, VerificarRostroView

urlpatterns = [
    path('registrar-embedding/', RegistrarEmbeddingView.as_view(), name='registrar-embedding'),
    path('verificar/', VerificarRostroView.as_view(), name='verificar-rostro'),
]