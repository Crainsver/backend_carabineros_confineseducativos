from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PerfilUsuario, Material, Mensaje, ProgresoEstudiante

class MaterialSerializer(serializers.ModelSerializer):
    url_pdf = serializers.SerializerMethodField()

    class Meta:
        model = Material
        fields = ['id', 'titulo', 'unidad', 'ramo', 'descripcion', 'archivo', 'url_pdf', 'fecha_creacion']
        extra_kwargs = {
            'archivo': {'required': False, 'write_only': True},
            'descripcion': {'required': False, 'allow_blank': True},
            'unidad': {'required': False, 'allow_blank': True},
            'ramo': {'required': False, 'allow_blank': True},
        }

    def get_url_pdf(self, obj):
        request = self.context.get('request')
        if obj.archivo:
            if request is not None:
                return request.build_absolute_uri(obj.archivo.url)
            return obj.archivo.url
        return obj.url_pdf or ""

class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = '__all__'

class RegistroSerializer(serializers.Serializer):
    nombreCompleto = serializers.CharField()
    correo = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    rol = serializers.ChoiceField(choices=['DOCENTE', 'ESTUDIANTE'], default='ESTUDIANTE')

    def create(self, validated_data):
        correo = validated_data['correo'].lower().strip()
        if User.objects.filter(username=correo).exists():
            raise serializers.ValidationError({"error": "El correo ya está registrado."})
        
        user = User.objects.create_user(
            username=correo,
            email=correo,
            password=validated_data['password']
        )
        PerfilUsuario.objects.create(
            user=user,
            nombre_completo=validated_data['nombreCompleto'],
            rol=validated_data['rol']
        )
        return user