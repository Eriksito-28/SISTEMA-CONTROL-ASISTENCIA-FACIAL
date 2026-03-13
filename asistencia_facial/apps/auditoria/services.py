"""
Función para registrar las acciones del usuario en auditoria
"""

from .models import Auditoria


#esta funcion crea un nuevo registro en la tabla de auditoria con informacion del
#usuario y recibe la accion que realizo el usuario, que accion, una descripcion y la ip
def registrar_auditoria(usuario, accion, descripcion, ip=None):
    auditoria = Auditoria.objects.create(
        usuario=usuario,
        accion=accion,
        descripcion=descripcion,
        ip=ip
    )
    return auditoria