from django.contrib import admin
from django.urls import path
from dispositivos.views import device_panel, device_detalle

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', device_panel, name="panel"),
    path('dispositivos/', device_panel, name="dispositivos"),
    path('dispositivos/<int:device_id>/', device_detalle, name="dispositivo"),
]
