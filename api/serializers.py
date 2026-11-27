from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PerfilUsuario, Material, Mensaje, ProgresoEstudiante

class MaterialSerializer(serializers.ModelSerializer):
    url_pdf = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = Material
        fields = '__all__'
        extra_kwargs = {
            'autor': {'required': False, 'allow_blank': True},
            'descripcion': {'required': False, 'allow_blank': True},
            'unidad': {'required': False, 'allow_blank': True},
            'ramo': {'required': False, 'allow_blank': True},
        }

    def create(self, validated_data):
        url_recibida = validated_data.pop('url_pdf', '') or validated_data.get('url_archivo', '')
        if not url_recibida or not str(url_recibida).strip().startswith(('http://', 'https://')):
            url_recibida = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

        campos_modelo = {f.name for f in Material._meta.get_fields()}
        if 'url_pdf' in campos_modelo:
            validated_data['url_pdf'] = url_recibida
        elif 'url_archivo' in campos_modelo:
            validated_data['url_archivo'] = url_recibida

        return super().create(validated_data)

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