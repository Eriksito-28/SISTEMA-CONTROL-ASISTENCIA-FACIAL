from rest_framework import serializers
from django.utils import timezone
from .models import Marcacion


class MarcacionSerializer(serializers.ModelSerializer):
    trabajador_nombre = serializers.SerializerMethodField()
    fecha = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

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

    def get_fecha(self, obj):
        fecha_local = timezone.localtime(obj.fecha)
        return fecha_local.strftime('%Y-%m-%dT%H:%M:%S%z')

    def get_created_at(self, obj):
        fecha_local = timezone.localtime(obj.created_at)
        return fecha_local.strftime('%Y-%m-%dT%H:%M:%S%z')