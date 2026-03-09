from rest_framework import serializers
from .models import Trabajador

#esta clase se usa para leer y mostrar datos de un trabajdor
class TrabajadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trabajador
        fields = [
            'id',
            'nombres',
            'apellido_paterno',
            'apellido_materno',
            'dni',
            'telefono',
            'cargo',
            'foto_url',
            'activo',
            'fecha_inicio_laboral',
            'fecha_fin_laboral',
            'fecha_registro',
        ]

#acá no está el campo embedding ni foto_url porque se agregarán 
#luego al implementar el reconocimiento facial 
class TrabajadorCrearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trabajador
        fields = [
            'nombres',
            'apellido_paterno',
            'apellido_materno',
            'dni',
            'telefono',
            'cargo',
            'fecha_inicio_laboral',
            'fecha_fin_laboral',
        ]

#esta clase se usa para poder modificar los datos de un trabajador que ya existe 
class TrabajadorActualizarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trabajador
        fields = [
            'nombres',
            'apellido_paterno',
            'apellido_materno',
            'telefono',
            'cargo',
            'fecha_inicio_laboral',
            'fecha_fin_laboral',
            'activo',
        ]