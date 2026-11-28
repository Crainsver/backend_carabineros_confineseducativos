from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Material, Mensaje, ProgresoEstudiante, PerfilUsuario
from .serializers import MaterialSerializer, MensajeSerializer, RegistroSerializer

# 1. REGISTRO (Público)
class RegistroView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"mensaje": "Usuario registrado con éxito"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 2. LOGIN CON JWT (Público)
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        correo = request.data.get('correo', '').lower().strip()
        password = request.data.get('password', '')

        user = authenticate(username=correo, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            perfil = getattr(user, 'perfil', None)
            return Response({
                "token": str(refresh.access_token),
                "nombreCompleto": perfil.nombre_completo if perfil else user.username,
                "rol": perfil.rol if perfil else "ESTUDIANTE",
                "correo": user.email
            }, status=status.HTTP_200_OK)
        return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)

# 3. MATERIALES POR UNIDAD (Protegido con JWT y soporte de archivos Multipart)
class MaterialListCreateView(generics.ListCreateAPIView):
    queryset = Material.objects.all().order_by('-fecha_creacion')
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

# 4. MENSAJES DOCENTE <-> ESTUDIANTE (Protegido con JWT)
class MensajeListCreateView(generics.ListCreateAPIView):
    queryset = Mensaje.objects.all().order_by('-fecha')
    serializer_class = MensajeSerializer
    permission_classes = [IsAuthenticated]

class ResponderMensajeView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            mensaje = Mensaje.objects.get(pk=pk)
            respuesta = request.data.get('respuesta', '')
            if respuesta:
                mensaje.respuesta = respuesta
                mensaje.respondido = True
                mensaje.save()
                return Response(MensajeSerializer(mensaje).data)
            return Response({"error": "La respuesta no puede estar vacía"}, status=400)
        except Mensaje.DoesNotExist:
            return Response({"error": "Mensaje no encontrado"}, status=404)

# 5. BARRA DE PROGRESO DEL ESTUDIANTE (Protegido con JWT)
class ProgresoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_materiales = Material.objects.count()
        completados = ProgresoEstudiante.objects.filter(estudiante=request.user, completado=True).count()
        porcentaje = (completados / total_materiales) if total_materiales > 0 else 0.0
        ids_completados = list(
            ProgresoEstudiante.objects.filter(estudiante=request.user, completado=True)
            .values_list('material_id', flat=True)
        )
        return Response({
            "total": total_materiales,
            "completados": completados,
            "porcentaje": round(porcentaje, 2),
            "idsCompletados": ids_completados
        })

    def post(self, request):
        material_id = request.data.get('material_id')
        try:
            material = Material.objects.get(pk=material_id)
            ProgresoEstudiante.objects.get_or_create(estudiante=request.user, material=material)
            return Response({"mensaje": "Progreso actualizado"}, status=status.HTTP_200_OK)
        except Material.DoesNotExist:
            return Response({"error": "Material no encontrado"}, status=status.HTTP_404_NOT_FOUND)