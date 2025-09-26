from django.contrib import admin
from .models import Category, Zone, Device, Measurement, Alert, Organization, Product, AlertRule, ProductAlertRule

# ─────────────────────────────────────────────────────────
# Reglas generales del sitio (NUEVO)
# ─────────────────────────────────────────────────────────
admin.site.site_header = "EcoEnergy — Admin"
admin.site.site_title = "EcoEnergy Admin"
admin.site.index_title = "Panel de administración"

# ─────────────────────────────────────────────────────────
# MAESTROS (globales)
# ─────────────────────────────────────────────────────────

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'status', 'created_at']
    search_fields = ['name']
    list_filter = ['status']
    ordering = ['name']
    list_per_page = 50

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
    list_display = ['name', 'category', 'zone', 'max_consumption', 'status', 'created_at']
    search_fields = ['name', 'category__name', 'zone__name']
    list_filter = ['status', 'category', 'zone']
    ordering = ['name']
    list_select_related = ['category', 'zone']
    list_per_page = 50

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