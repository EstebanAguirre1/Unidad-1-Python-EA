from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dispositivos import views as disp_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views

urlpatterns = [
    # --- Panel de administración ---
    path('admin/', admin.site.urls),

    # --- Página principal protegida (Dashboard) ---
    path('', login_required(disp_views.dashboard), name='dashboard'),

    # --- Rutas principales de apps ---
    path('dispositivos/', include('dispositivos.urls')),  # CRUD de dispositivos y zonas
    path('', include('usuarios.urls')),  # Login, logout, registro, perfil

    # --- Listados adicionales protegidos ---
    path('mediciones/', login_required(disp_views.listado_mediciones), name='listado_mediciones'),
    path('alertas/', login_required(disp_views.listado_alertas), name='listado_alertas'),

    # --- Logout del admin (redirige al login del admin, no al del proyecto) ---
    path('admin/logout/', auth_views.LogoutView.as_view(next_page='/admin/login/'), name='admin_logout'),
]

# --- Archivos estáticos y de medios ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
