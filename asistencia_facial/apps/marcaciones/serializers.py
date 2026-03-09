from rest_framework import serializers
from .models import Marcacion


class MarcacionSerializer(serializers.ModelSerializer):
    trabajador_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Marcacion
        fields = [
            'id',
            'trabajador',
            'trabajador_nombre',
            'fecha',
            'tipo',
            'estado',
            'ip',
            'dispositivo',
            'exitoso',
            'created_at',
        ]

    def get_trabajador_nombre(self, obj):
        return f'{obj.trabajador.nombres} {obj.trabajador.apellido_paterno}'