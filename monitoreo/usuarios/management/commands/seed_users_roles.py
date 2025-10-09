from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import transaction

# Ajusta el import según tu app y modelo real
from usuarios.models import Usuario
from dispositivos.models import Organization
from usuarios.models import Role  # modelo que conecta a Group

# =========================
# CONFIG ECOENERGY
# =========================
USERS = [
    {
        "username": "admin",
        "email": "admin@ecoenergy.com",
        "password": "admin123",
        "role": "EcoEnergy - Admin",  # coincide con la seed del profe
        "organization": "EcoEnergy",
        "first_name": "Admin",
        "last_name": "Global",
    },
    {
        "username": "kevin",
        "email": "kevin@ecoenergy.com",
        "password": "kevin123",
        "role": "Cliente - Electrónico",  # rol limitado
        "organization": "EcoEnergy",
        "first_name": "Kevin",
        "last_name": "Cliente",
    },
]

class Command(BaseCommand):
    help = "Siembra usuarios base para EcoEnergy (sin tocar roles/módulos existentes)"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # Buscamos la organización existente "EcoEnergy" o la creamos si no está
        org, _ = Organization.objects.get_or_create(name="EcoEnergy")

        for udata in USERS:
            # 1) Crear usuario de Django
            user, created = User.objects.get_or_create(username=udata["username"], defaults={
                "email": udata["email"],
                "first_name": udata["first_name"],
                "last_name": udata["last_name"],
                "is_staff": True,  # para poder entrar al admin
                "is_superuser": udata["role"] == "EcoEnergy - Admin",
            })
            if created:
                user.set_password(udata["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Usuario Django creado: {user.username}"))

            # 2) Conectar con Usuario (perfil)
            role = Role.objects.get(group__name=udata["role"])
            usuario, _ = Usuario.objects.get_or_create(user=user, defaults={
                "organization": org,
                "role": role,
                "rut": "21452932-1",
                "telefono": "",
                "direccion": "",
            })

            # 3) Asegurarse de asignar el grupo correcto al User
            user.groups.clear()
            user.groups.add(role.group)

            self.stdout.write(self.style.SUCCESS(f"Perfil Usuario listo: {user.username} ({role.group.name})"))

        self.stdout.write(self.style.SUCCESS("Seed de usuarios completada"))

