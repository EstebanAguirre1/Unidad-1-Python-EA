from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from dispositivos import views as disp_views
from dispositivos.views import (
    dashboard,               # Panel principal
    listado_dispositivos,    # Listado de dispositivos
    detalle_dispositivo,     # Detalle de un dispositivo
    listado_mediciones,      # Listado global de mediciones
    listado_alertas          # Resumen/listado de alertas
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dispositivos.urls')),
    # Dashboard / panel principal
    path('', login_required(dashboard), name='dashboard'),

    # Dispositivos
    path('dispositivos/', listado_dispositivos, name='listado_dispositivos'),
    path('dispositivos/<int:device_id>/', detalle_dispositivo, name='detalle_dispositivo'),
    path('dispositivos/', include('dispositivos.urls')),

    # Mediciones
    path('mediciones/', listado_mediciones, name='listado_mediciones'),

    # Alertas
    path('alertas/', listado_alertas, name='listado_alertas'),

    # Usuarios
    path('usuarios/', include('usuarios.urls')),
    path('', login_required(disp_views.dashboard), name='dashboard'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)