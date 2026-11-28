from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    ROLES = (
        ('DOCENTE', 'Docente'),
        ('ESTUDIANTE', 'Estudiante'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    nombre_completo = models.CharField(max_length=150)
    rol = models.CharField(max_length=20, choices=ROLES, default='ESTUDIANTE')

    def __str__(self):
        return f"{self.nombre_completo} ({self.rol})"

class Material(models.Model):
    titulo = models.CharField(max_length=200)
    unidad = models.CharField(max_length=100)
    ramo = models.CharField(max_length=100, default="Procedimientos Policiales")
    descripcion = models.TextField()
    archivo = models.FileField(upload_to='materiales/', null=True, blank=True)
    url_pdf = models.CharField(max_length=500, blank=True, default="")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.unidad} - {self.titulo}"

class Mensaje(models.Model):
    remitente_nombre = models.CharField(max_length=150)
    rol_remitente = models.CharField(max_length=20)
    asignatura = models.CharField(max_length=100)
    pregunta = models.TextField()
    respuesta = models.TextField(blank=True, default="")
    respondido = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

class ProgresoEstudiante(models.Model):
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    completado = models.BooleanField(default=True)

    class Meta:
        unique_together = ('estudiante', 'material')