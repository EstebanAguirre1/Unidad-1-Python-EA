from django.shortcuts import render, get_object_or_404
from .models import Device, Measurement, Alert, Category
from usuarios.models import Usuario
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.decorators.cache import never_cache

def device_panel(request):
    devices = Device.objects.select_related("category")
    return render(request, "dispositivos/panel.html", {"devices": devices})

def device_detalle(request, device_id):
    device = Device.objects.get(id=device_id)
    return render(request, "dispositivos/detalle.html", {"device": device})


@login_required
@never_cache
def dashboard(request):
    # Obtener usuario y organización
    try:
        usuario = Usuario.objects.get(user=request.user)
        org = usuario.organization
    except Usuario.DoesNotExist:
        usuario = None
        org = None

    # Últimas 10 mediciones
    ultimas_10_mediciones = Measurement.objects.select_related('device').order_by('-created_at')[:10]

    # Alertas de la última semana
    hace_una_semana = timezone.now() - timedelta(days=7)
    alertas_semana = Alert.objects.filter(created_at__gte=hace_una_semana)

    # Agrupar alertas por severidad (alert_status)
    alertas_por_severidad = alertas_semana.values('alert_status').annotate(total=Count('id')).order_by('-total')

    # Dispositivos por categoría
    dispositivos_por_categoria = Device.objects.values('category').annotate(total=Count('id')).order_by('-total')

    # Dispositivos por zona
    dispositivos_por_zona = Device.objects.values('zone').annotate(total=Count('id')).order_by('-total')

    # Totales globales
    total_dispositivos = Device.objects.count()
    total_alertas_semana = alertas_semana.count()

    context = {
        'usuario': usuario,
        'org': org,
        'ultimas_10_mediciones': ultimas_10_mediciones,
        'alertas_por_severidad': alertas_por_severidad,
        'dispositivos_por_categoria': dispositivos_por_categoria,
        'dispositivos_por_zona': dispositivos_por_zona,
        'total_dispositivos': total_dispositivos,
        'total_alertas_semana': total_alertas_semana,
    }

    return render(request, "dispositivos/dashboard.html", context)

@login_required
@never_cache
def listado_dispositivos(request):
    # Obtener todas las categorías únicas
    categorias = Device.objects.values_list('category', flat=True).distinct()

    # Filtrar por categoría si se recibe por GET
    categoria_seleccionada = request.GET.get('categoria')
    if categoria_seleccionada:
        dispositivos = Device.objects.filter(category=categoria_seleccionada)
    else:
        dispositivos = Device.objects.all()

    context = {
        'dispositivos': dispositivos,
        'categorias': categorias,
        'categoria_seleccionada': categoria_seleccionada,
    }
    return render(request, 'dispositivos/listado_dispositivos.html', context)

@login_required
@never_cache
def detalle_dispositivo(request, device_id):
    device = get_object_or_404(Device, id=device_id)
    mediciones = Measurement.objects.filter(device=device).order_by('-created_at')
    alertas = Alert.objects.filter(device=device).order_by('-created_at')

    context = {
        'device': device,
        'mediciones': mediciones,
        'alertas': alertas
    }
    return render(request, "dispositivos/detalle_dispositivo.html", context)

@login_required
@never_cache
def listado_mediciones(request):
    mediciones = Measurement.objects.select_related('device').order_by('-created_at')
    return render(request, "dispositivos/listado_mediciones.html", {"mediciones": mediciones})

@login_required
@never_cache
def listado_alertas(request):
    alertas = Alert.objects.select_related('device').order_by('-created_at')
    return render(request, "dispositivos/listado_alertas.html", {"alertas": alertas})

