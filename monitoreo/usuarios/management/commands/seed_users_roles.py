from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

from usuarios.models import Usuario, Role
from dispositivos.models import Organization, Device, Category, Zone

# =========================
# CONFIG ECOENERGY
# =========================
USERS = [
    {
        "username": "admin",
        "email": "admin@ecoenergy.com",
        "password": "admin123",
        "role": "EcoEnergy - Admin",
        "organization": "EcoEnergy",
        "first_name": "Admin",
        "last_name": "Global",
        "rut": "21453932-1",
    },
    {
        "username": "kevin",
        "email": "kevin@ecoenergy.com",
        "password": "kevin123",
        "role": "Cliente - Electrónico",
        "organization": "EcoEnergy",
        "first_name": "Kevin",
        "last_name": "Cliente",
        "rut": "21453933-2",
    },
]

DEVICES = [
    {"name": "Sensor Temperatura", "max_consumption": 500, "power": 50},
    {"name": "Sensor Humedad", "max_consumption": 300, "power": 30},
    {"name": "Medidor Consumo", "max_consumption": 1000, "power": 220},
]

class Command(BaseCommand):
    help = "Siembra usuarios base y dispositivos para EcoEnergy"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # Crear o obtener organización
        org, _ = Organization.objects.get_or_create(name="EcoEnergy")
        self.stdout.write(self.style.SUCCESS(f"Organización lista: {org.name}"))

        # =========================
        # Crear usuarios
        # =========================
        for udata in USERS:
            user, created = User.objects.get_or_create(
                username=udata["username"],
                defaults={
                    "email": udata["email"],
                    "first_name": udata["first_name"],
                    "last_name": udata["last_name"],
                    "is_staff": True,
                    "is_superuser": udata["role"] == "EcoEnergy - Admin",
                },
            )
            if created:
                user.set_password(udata["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Usuario Django creado: {user.username}"))

            role = Role.objects.get(group__name=udata["role"])
            usuario, _ = Usuario.objects.get_or_create(
                user=user,
                defaults={
                    "organization": org,
                    "role": role,
                    "rut": udata["rut"],
                    "telefono": "",
                    "direccion": "",
                },
            )

            user.groups.clear()
            user.groups.add(role.group)
            self.stdout.write(self.style.SUCCESS(f"Perfil Usuario listo: {user.username} ({role.group.name})"))

        # =========================
        # Crear categoría y zona base
        # =========================
        category, _ = Category.objects.get_or_create(name="Sensores", organization=org)
        zone, _ = Zone.objects.get_or_create(name="Planta Principal", organization=org)

        # =========================
        # Crear dispositivos
        # =========================
        for ddata in DEVICES:
            device, created = Device.objects.get_or_create(
                name=ddata["name"],
                organization=org,
                defaults={
                    "category": category,
                    "zone": zone,
                    "max_consumption": ddata["max_consumption"],
                    "power": ddata["power"],
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Dispositivo creado: {device.name}"))

        self.stdout.write(self.style.SUCCESS("Seed de usuarios y dispositivos completada"))
