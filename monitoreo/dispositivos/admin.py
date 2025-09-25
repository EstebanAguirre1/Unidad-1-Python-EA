from django.contrib import admin
from .models import Category, Zone, Device, Measurement, Alert, Organization, Product, AlertRule, ProductAlertRule

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'status']
    search_fields = ['name']
    list_filter = ['status']
    ordering = ['name']

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'organization', 'status']
    search_fields = ['name', 'organization__name']
    list_filter = ['status', 'organization']
    ordering = ['name']
    list_select_related = ['organization']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'organization', 'status']
    search_fields = ['name', 'organization__name']
    list_filter = ['status', 'organization']
    ordering = ['name']
    list_select_related = ['organization']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'category', 'manufacturer', 'nominal_voltage_v', 'status']
    search_fields = ['name', 'sku', 'category__name', 'manufacturer']
    list_filter = ['status', 'category']
    ordering = ['name']
    list_select_related = ['category']

@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'severity', 'unit', 'default_min_threshold', 'default_max_threshold', 'status']
    search_fields = ['name']
    list_filter = ['status', 'severity']
    ordering = ['name']

@admin.register(ProductAlertRule)
class ProductAlertRuleAdmin(admin.ModelAdmin):
    list_display = ['product', 'alert_rule', 'min_threshold', 'max_threshold', 'status']
    search_fields = ['product__name', 'alert_rule__name']
    list_filter = ['status']
    ordering = ['product__name']
    list_select_related = ['product', 'alert_rule']

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'zone', 'max_consumption', 'status']
    search_fields = ['name', 'category__name', 'zone__name']
    list_filter = ['status', 'category', 'zone']
    ordering = ['name']
    list_select_related = ['category', 'zone']

@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ['device', 'value', 'measured_at', 'status']
    search_fields = ['device__name']
    list_filter = ['status', 'measured_at']
    ordering = ['-measured_at']  # Más recientes primero
    date_hierarchy = 'measured_at'  # Navegación por fechas
    list_select_related = ['device']

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['device', 'type', 'alert_status', 'triggered_at', 'status']
    search_fields = ['device__name', 'type', 'message']
    list_filter = ['status', 'alert_status', 'type', 'triggered_at']
    ordering = ['-triggered_at']  # Más recientes primero
    date_hierarchy = 'triggered_at'  # Navegación por fechas
    list_select_related = ['device']