from .models import Auditoria


#esta funcion recibe la accion que realizo el usuairo, que accion, una descripcion y la ip 
def registrar_auditoria(usuario, accion, descripcion, ip=None):
    auditoria = Auditoria.objects.create(
        usuario=usuario,
        accion=accion,
        descripcion=descripcion,
        ip=ip
    )
    return auditoria