from django.shortcuts import redirect, render, get_object_or_404
from .models import Device, Measurement, Alert, Category, Zone
from usuarios.models import Usuario
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.decorators.cache import never_cache
from django.contrib import messages
from monitoreo.decorators import permission_or_redirect
from django.views.decorators.http import require_POST
from .forms import ZoneForm, DeviceForm
from dispositivos.models import Zone
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def add_to_cart(request, product_id):
    product = get_object_or_404(Device, id=product_id)

    # Ejemplo de lógica: stock > 0 permite agregar, si no, error
    if hasattr(product, 'stock') and product.stock > 0:
        # uso product.name (tu modelo usa 'name')
        messages.success(request, f'Producto "{product.name}" agregado al carrito 🛒.')
    else:
        messages.error(request, f'Stock insuficiente para "{product.name}" 😢.')

    return redirect('inicio')  # redirige a donde está tu dashboard o página principal


@login_required
@never_cache
def inicio(request):
    # Contador de visitas
    visitas = request.session.get('visitas', 0)
    request.session['visitas'] = visitas + 1

    # Obtener dispositivos reales desde la base de datos
    dispositivos = Device.objects.all()

    # Producto de ejemplo guardado en sesión (opcional)
    if 'producto' not in request.session:
        request.session['producto'] = {
            'nombre': 'Sensor de Temperatura',
            'sku': 'SKU123',
            'stock': 3
        }

    producto = request.session['producto']

    # Si se presiona el botón del formulario (el del producto de sesión)
    if request.method == 'POST':
        if producto['stock'] > 0:
            producto['stock'] -= 1  # restar 1 al stock
            request.session['producto'] = producto
            request.session.modified = True
            messages.success(request, f"{producto['nombre']} agregado al carrito 🛒")
        else:
            messages.error(request, "Stock insuficiente ❌")

        return redirect('inicio')  # recargar la página

    # Renderizar el template con ambos: dispositivos y producto
    return render(request, 'dispositivos/dashboard.html', {
        'visitas': visitas,
        'producto': producto,
        'dispositivos': dispositivos
    })


@login_required
@never_cache
def dashboard(request):
    # Contador de visitas
    visitas = request.session.get('visitas', 0)
    request.session['visitas'] = visitas + 1

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
        'visitas': visitas,  # 👈 Agregamos el contador aquí
    }

    return render(request, "dispositivos/dashboard.html", context)


# ------------------------------------------------------------
# LISTADO DISPOSITIVOS (fusionado: filtro por categoria + permisos)
# ------------------------------------------------------------
@login_required
@permission_or_redirect('dispositivos.view_device', 'dashboard', "No tienes permiso para ver dispositivos.")
def listado_dispositivos(request):
    categorias = Category.objects.all()
    categoria_seleccionada = request.GET.get('categoria', '')

    # Filtro por categoría
    dispositivos = Device.objects.all()
    if categoria_seleccionada:
        dispositivos = dispositivos.filter(category_id=categoria_seleccionada)

    # Ordenamiento por columna
    sort = request.GET.get('sort', 'name')
    direction = request.GET.get('direction', 'asc')
    
    sort_fields = {
        'name': 'name',
        'category': 'category__name',
        'zone': 'zone__name',
        'organization': 'organization__name',
    }
    
    if sort in sort_fields:
        field = sort_fields[sort]
        if direction == 'desc':
            field = '-' + field
        dispositivos = dispositivos.order_by(field)

    # Paginación
    try:
        page_size = int(request.GET.get('page_size', 5))
    except (ValueError, TypeError):
        page_size = 5
    page_sizes = [5, 15, 30]

    paginator = Paginator(dispositivos, page_size)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'dispositivos': page_obj.object_list,
        'categorias': categorias,
        'categoria_seleccionada': categoria_seleccionada,
        'sort': sort,
        'direction': direction,
        'page_obj': page_obj,
        'page_size': page_size,
        'page_sizes': page_sizes,
    }

    return render(request, "dispositivos/listado_dispositivos.html", context)


@login_required
@never_cache
def detalle_dispositivo(request, device_id):
    device = get_object_or_404(Device, id=device_id)
    mediciones = Measurement.objects.filter(device=device).order_by('-measured_at')
    alertas = Alert.objects.filter(device=device).order_by('-triggered_at')

    context = {
        'device': device,
        'mediciones': mediciones,
        'alertas': alertas,
    }
    return render(request, "dispositivos/detalle_dispositivo.html", context)



# ------------------------------------------------------------
# CRUD Dispositivo (create / edit / delete_ajax)
# ------------------------------------------------------------
@login_required
@permission_or_redirect('dispositivos.add_device', 'listado_dispositivos', "No tienes permiso para agregar dispositivos.")
def dispositivo_create(request):
    if request.method == "POST":
        # recibir files también si subes imagen
        form = DeviceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Dispositivo creado correctamente")
            return redirect("listado_dispositivos")
        else:
            messages.error(request, "Corrige los errores del formulario")
    else:
        form = DeviceForm()
    return render(request, "dispositivos/dispositivos_form.html", {"form": form, "accion": "Crear"})


@login_required
@permission_or_redirect('dispositivos.change_device', 'listado_dispositivos', "No tienes permiso para editar dispositivos.")
def dispositivo_edit(request, pk):
    dispositivo = get_object_or_404(Device, pk=pk)
    if request.method == "POST":
        form = DeviceForm(request.POST, request.FILES, instance=dispositivo)
        if form.is_valid():
            form.save()
            messages.success(request, "Dispositivo actualizado correctamente")
            return redirect("listado_dispositivos")
        else:
            messages.error(request, "Corrige los errores del formulario")
    else:
        form = DeviceForm(instance=dispositivo)
    return render(request, "dispositivos/dispositivos_form.html", {"form": form, "accion": "Editar"})


@login_required
@require_POST
@permission_or_redirect('dispositivos.delete_device', 'listado_dispositivos', "No tienes permiso para eliminar dispositivos.")
def dispositivo_delete_ajax(request, pk):
    if not request.headers.get("x-requested-with") == "XMLHttpRequest":
        return HttpResponseBadRequest("Solo AJAX")
    dispositivo = get_object_or_404(Device, pk=pk)
    # usar name (campo real del modelo)
    nombre = dispositivo.name
    dispositivo.delete()
    return JsonResponse({"ok": True, "message": f"Dispositivo '{nombre}' eliminado"})


# ------------------------------------------------------------
# Zonas (mantengo todas tus vistas originales, sin cambios lógicos)
# ------------------------------------------------------------
@login_required
@permission_or_redirect('dispositivos.view_zone', 'dashboard', "No tienes permiso para ver zonas.")
def zona_list(request):
    # --- Parámetros de búsqueda y ordenamiento ---
    q = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "name")
    direction = request.GET.get("direction", "asc")
    paginate_by = int(request.GET.get("paginate_by", 5))

    # --- Consulta base ---
    zonas = Zone.objects.select_related("organization").all()

    # --- Filtrar búsqueda ---
    if q:
        zonas = zonas.filter(
            Q(name__icontains=q) |
            Q(organization__name__icontains=q)
        )

    # --- Ordenamiento ---
    order_prefix = "" if direction == "asc" else "-"
    if sort == "organization":
        zonas = zonas.order_by(f"{order_prefix}organization__name")
    else:
        zonas = zonas.order_by(f"{order_prefix}{sort}")

    # --- Paginación ---
    paginator = Paginator(zonas, paginate_by)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # --- Mantener parámetros en querystring ---
    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    # --- Opciones de paginador ---
    paginate_options = [5, 15, 30]

    context = {
        "page_obj": page_obj,
        "q": q,
        "sort": sort,
        "direction": direction,
        "paginate_by": paginate_by,
        "paginate_options": paginate_options,
        "querystring": querystring,
    }

    return render(request, "dispositivos/zonas_list.html", context)

@login_required
@permission_or_redirect('dispositivos.add_zone', 'zona_list', "No tienes permiso para crear zonas.")
def zona_create(request):
    if request.method == "POST":
        form = ZoneForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Zona creada exitosamente")
            return redirect("zona_list")
        else:
            messages.error(request, "Por favor corrige los errores")
    else:
        form = ZoneForm()
    return render(request, "dispositivos/zona_form.html", {"form": form, "accion": "Crear"})


@login_required
@permission_or_redirect('dispositivos.change_zone', 'zona_list', "No tienes permiso para editar zonas.")
def zona_edit(request, pk):
    zona = get_object_or_404(Zone, pk=pk)
    if request.method == "POST":
        form = ZoneForm(request.POST, instance=zona)
        if form.is_valid():
            form.save()
            messages.success(request, "Zona actualizada correctamente")
            return redirect("zona_list")
        else:
            messages.error(request, "Corrige los errores antes de guardar")
    else:
        form = ZoneForm(instance=zona)
    return render(request, "dispositivos/zona_form.html", {"form": form, "accion": "Editar"})


@login_required
@permission_or_redirect('dispositivos.delete_zone', 'zona_list', "No tienes permiso para eliminar zonas.")
def zona_delete(request, pk):
    zona = get_object_or_404(Zone, pk=pk)
    zona.delete()
    messages.warning(request, f"La zona '{zona.name}' fue eliminada")
    return redirect("zona_list")


@login_required
@require_POST
@permission_or_redirect('dispositivos.delete_zone', 'zona_list', "No tienes permiso para eliminar zonas.")
def zona_delete_ajax(request, pk):
    """
    Elimina una zona y responde JSON para que el frontend actualice la UI sin recargar.
    """
    # Verifica que la petición sea AJAX
    if not request.headers.get("x-requested-with") == "XMLHttpRequest":
        return HttpResponseBadRequest("Solo AJAX")
    # Verifica permisos y autenticación con pk de zona
    zona = get_object_or_404(Zone, pk=pk)
    nombre = zona.name
    zona.delete()
    return JsonResponse({"ok": True, "message": f"Zona '{nombre}' eliminada"})


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


def error_403(request, exception=None):
    return render(request, '403.html', status=403)

def error_404(request, exception=None):
    return render(request, '404.html', status=404)