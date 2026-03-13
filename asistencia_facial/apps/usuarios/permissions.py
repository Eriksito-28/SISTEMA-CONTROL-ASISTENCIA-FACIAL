from rest_framework.permissions import BasePermission

class EsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.rol.nombre == 'ADMIN'

class EsTrabajador(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.rol.nombre == 'TRABAJADOR'

class EsAdminOTrabajador(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.rol.nombre in ['ADMIN', 'TRABAJADOR']