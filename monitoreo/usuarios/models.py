from django.contrib.auth.models import Group
from django.conf import settings
from django.db import models
from dispositivos.models import Organization


def avatar_upload_path(instance, filename):
    return f"avatars/user_{instance.user.id}/{filename}"

class Usuario(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    rut = models.CharField(max_length=12, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, null=True)  # <--- Nuevo campo

    # Conecta con el rol real
    role = models.ForeignKey('Role', null=True, blank=True, on_delete=models.SET_NULL, related_name="usuarios")

    def __str__(self):
        return f"{self.user.username} @ {self.organization.name}"



class Module(models.Model):
    code = models.SlugField(max_length=50, unique=True)
            #'ventas', 'empleados'
    name = models.CharField(max_length=100)
            #'Ventas', 'empleados'
    icon = models.CharField(max_length=50, blank=True)
            # Opcional para el menu
    
    def __str__(self):
        return self.name
    

class Role(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="role")

    def __str__(self):
        return self.group.name


class RoleModulePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="module_perms")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="role_perms")
    can_view = models.BooleanField(default=False)
    can_add = models.BooleanField(default=False)
    can_change = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ("role", "module")

    def __str__(self):
        return f"{self.role} -> {self.module} (v:{self.can_view}/a:{self.can_add}/c:{self.can_change}/d:{self.can_delete})"
