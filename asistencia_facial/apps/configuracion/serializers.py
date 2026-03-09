from rest_framework import serializers
from .models import ConfiguracionSistema

#los campos qeu se va a poder ver y actualizar desde la configuracion  
class ConfiguracionSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionSistema
        fields = [
            'id',
            'hora_inicio_entrada',
            'hora_fin_entrada',
            'hora_inicio_salida',
            'hora_fin_salida',
            'max_intentos',
            'max_intentos_faciales',
            'umbral_similitud',
            'created_at',
        ]