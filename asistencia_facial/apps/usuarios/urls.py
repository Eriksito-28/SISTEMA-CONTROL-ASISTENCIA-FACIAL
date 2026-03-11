from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView,
    LogoutView,
    CambiarPasswordView,
    DesbloquearUsuarioView,
    ResetearIntentosFacialesView,
    ListarUsuariosView
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('cambiar-password/', CambiarPasswordView.as_view(), name='cambiar_password'),
    path('desbloquear/<int:pk>/', DesbloquearUsuarioView.as_view(), name='desbloquear_usuario'),
    path('resetear-intentos/<int:pk>/', ResetearIntentosFacialesView.as_view(), name='resetear_intentos'),
    path('listar/', ListarUsuariosView.as_view(), name='listar_usuarios'),
]