from django.contrib import admin
from .models import Organization
from dispositivos.models import Zone 
from .forms import OrganizationForm # ← formulario personalizado

class ZoneInline(admin.TabularInline):  # ojo: Inline con "l" minúscula
    model = Zone
    extra = 0
    fields = ("name", "status")
    show_change_link = True

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    list_filter = ['name']
    ordering = ("name",)   # tupla correcta
    list_per_page = 50
    inlines = [ZoneInline]
    form = OrganizationForm # <<--- usamos el form con validaciones
