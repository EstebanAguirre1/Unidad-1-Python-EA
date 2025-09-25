from django.contrib import admin
from .models import Category, Zone, Device, Measurement, Alert

admin.site.register(Zone)
admin.site.register(Category)
admin.site.register(Measurement)
admin.site.register(Alert)

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ["name", "max_consumption", "status", "category"]
    list_filter = ["status", "category"]
    search_fields = ["name",]



