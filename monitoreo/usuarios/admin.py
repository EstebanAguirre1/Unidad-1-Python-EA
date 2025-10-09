from django.contrib import admin
from .models import Usuario , Module, Role, RoleModulePermission

@admin.register(Usuario)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_staff', 'organization', 'role', 'rut', 'telefono', 'direccion')
    list_filter = ('organization', 'role', 'user__is_staff')  # filtro por staff
    search_fields = ('user__username', 'rut', 'role__group__name')

    # Si quieres mostrarlo como un campo "booleano" con iconitos de check/cross:
    def is_staff(self, obj):
        return obj.user.is_staff
    is_staff.boolean = True
    is_staff.short_description = 'Staff'


# --- Module ---
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'icon')  # columnas que se mostrarán en la lista
    search_fields = ('code', 'name')         # campos por los que se puede buscar

# --- Role ---
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('group',)  # solo mostramos el nombre del grupo
    search_fields = ('group__name',)  # búsqueda por nombre del grupo

# --- RoleModulePermission ---
@admin.register(RoleModulePermission)
class RoleModulePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'module', 'can_view', 'can_add', 'can_change', 'can_delete')
    list_filter = ('role', 'module')  # filtros a la izquierda
    search_fields = ('role__group__name', 'module__name')  # búsqueda por rol o módulo