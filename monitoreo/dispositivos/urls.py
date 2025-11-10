from django.urls import path
from . import views

urlpatterns = [
    # --- Inicio y carrito ---
    path('inicio/', views.inicio, name='inicio'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    # --- CRUD de Dispositivos ---
    path('', views.listado_dispositivos, name='listado_dispositivos'),
    path('nuevo/', views.dispositivo_create, name='dispositivo_create'),
    path('editar/<int:pk>/', views.dispositivo_edit, name='dispositivo_edit'),
    path('eliminar/<int:pk>/', views.dispositivo_delete_ajax, name='dispositivo_delete_ajax'),
    path('<int:device_id>/', views.detalle_dispositivo, name='detalle_dispositivo'),

    # --- CRUD de Zonas ---
    path('zonas/', views.zona_list, name='zona_list'),
    path('zonas/nueva/', views.zona_create, name='zona_create'),
    path('zonas/editar/<int:pk>/', views.zona_edit, name='zona_edit'),
    path('zonas/<int:pk>/delete/', views.zona_delete_ajax, name='zona_delete_ajax'),
]
