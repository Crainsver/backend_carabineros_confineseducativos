from django.urls import path
from .views import (
    RegistroView, LoginView, MaterialListCreateView,
    MensajeListCreateView, ResponderMensajeView, ProgresoView
)

urlpatterns = [
    path('auth/registro', RegistroView.as_view(), name='registro'),
    path('auth/login', LoginView.as_view(), name='login'),
    path('materiales', MaterialListCreateView.as_view(), name='materiales'),
    path('mensajes', MensajeListCreateView.as_view(), name='mensajes'),
    path('mensajes/<int:pk>/responder', ResponderMensajeView.as_view(), name='responder-mensaje'),
    path('progreso', ProgresoView.as_view(), name='progreso'),
]