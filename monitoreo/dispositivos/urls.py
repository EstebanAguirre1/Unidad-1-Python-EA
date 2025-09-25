# dispositivos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # dashboard principal
    path('devices/', views.listado_dispositivos, name='listado_dispositivos'),
    path('devices/<int:device_id>/', views.detalle_dispositivo, name='detalle_dispositivo'),
]
