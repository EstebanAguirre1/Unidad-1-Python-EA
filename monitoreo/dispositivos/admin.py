from django.contrib import admin
from dispositivos.models import Device
from usuarios.models import Usuario
from .models import Category, Zone, Device, Measurement, Alert, Product, AlertRule, ProductAlertRule

# ─────────────────────────────────────────────────────────
# Reglas generales del sitio (NUEVO)
# ─────────────────────────────────────────────────────────
admin.site.site_header = "EcoEnergy — Admin"
admin.site.site_title = "EcoEnergy Admin"
admin.site.index_title = "Panel de administración"

# ─────────────────────────────────────────────────────────
# ACCIONES PERSONALIZADAS
# ─────────────────────────────────────────────────────────
@admin.action(description="Activar dispositivos seleccionados")
def make_active(modeladmin, request, queryset):
    queryset.update(status="ACTIVE")

@admin.action(description="Desactivar dispositivos seleccionados")
def make_inactive(modeladmin, request, queryset):
    queryset.update(status="INACTIVE")


# ─────────────────────────────────────────────────────────
# MAESTROS (globales)
# ─────────────────────────────────────────────────────────

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'organization', 'status', 'created_at']
    search_fields = ['name', 'organization__name']
    list_filter = ['status', 'organization']
    ordering = ['name']
    list_select_related = ['organization']
    list_per_page = 50

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'organization', 'status', 'created_at']
    search_fields = ['name', 'organization__name']
    list_filter = ['status', 'organization']
    ordering = ['name']
    list_select_related = ['organization']
    list_per_page = 50

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'category', 'manufacturer', 'nominal_voltage_v', 'status', 'created_at']
    search_fields = ['name', 'sku', 'category__name', 'manufacturer']
    list_filter = ['status', 'category']
    ordering = ['name']
    list_select_related = ['category']
    list_per_page = 50

@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'severity', 'unit', 'default_min_threshold', 'default_max_threshold', 'status', 'created_at']
    search_fields = ['name']
    list_filter = ['status', 'severity']
    ordering = ['name']
    list_per_page = 50

@admin.register(ProductAlertRule)
class ProductAlertRuleAdmin(admin.ModelAdmin):
    list_display = ['product', 'alert_rule', 'min_threshold', 'max_threshold', 'status', 'created_at']
    search_fields = ['product__name', 'alert_rule__name']
    list_filter = ['status']
    ordering = ['product__name']
    list_select_related = ['product', 'alert_rule']
    list_per_page = 50



@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    # Columnas que se muestran en la lista
    list_display = [
        'name', 'organization', 'category', 'zone', 'power', 'max_consumption',
        'status', 'created_at'
    ]
    # Campos por los que se puede buscar
    search_fields = ['name', 'category__name', 'zone__name']
    # Filtros laterales
    list_filter = ['status', 'category', 'zone']
    # Orden por defecto
    ordering = ['name']
    # Optimización: carga relacionada
    list_select_related = ['category', 'zone']
    # Paginación
    list_per_page = 50
    # Acciones personalizadas
    actions = [make_active, make_inactive]

    # 🔹 Filtrar los objetos que aparecen en la lista del admin
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            return qs.filter(organization=request.user.usuario.organization)
        except AttributeError:
            return qs.none()

    # 🔹 Limitar opciones en los selects (zone, category) al editar/crear
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            try:
                org = request.user.usuario.organization
                if db_field.name == "zone":
                    kwargs["queryset"] = Zone.objects.filter(organization=org)
                elif db_field.name == "category":
                    kwargs["queryset"] = Category.objects.filter(organization=org)
            except AttributeError:
                kwargs["queryset"] = db_field.related_model.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)





@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ['device', 'value', 'measured_at', 'status', 'created_at']
    search_fields = ['device__name']
    list_filter = ['status', 'measured_at']
    ordering = ['-measured_at']
    date_hierarchy = 'measured_at'
    list_select_related = ['device']
    list_per_page = 50

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['device', 'type', 'alert_status', 'triggered_at', 'status', 'created_at']
    search_fields = ['device__name', 'type', 'message']
    list_filter = ['status', 'alert_status', 'type', 'triggered_at']
    ordering = ['-triggered_at']
    date_hierarchy = 'triggered_at'
    list_select_related = ['device']
    list_per_page = 50