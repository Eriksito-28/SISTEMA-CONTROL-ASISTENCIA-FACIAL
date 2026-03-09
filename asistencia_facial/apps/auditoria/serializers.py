from rest_framework import serializers
from .models import Auditoria


#se agrega un campo para que el fron reciba el nombre completo del usuario si hacer consulas demas 
class AuditoriaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Auditoria
        fields = [
            'id',
            'usuario',
            'usuario_nombre',
            'accion',
            'descripcion',
            'fecha',
            'ip',
        ]

    def get_usuario_nombre(self, obj):
        return f'{obj.usuario.trabajador.nombres} {obj.usuario.trabajador.apellido_paterno}'