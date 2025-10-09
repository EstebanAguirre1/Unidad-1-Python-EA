# accounts/management/commands/seed_roles_modules.py
# ------------------------------------------------------------
# Siembra para EcoEnergy:
# - Crea/actualiza MÓDULOS (operacion, catalogo, organizacion)
# - Crea/actualiza ROLES como Groups de Django:
#     * Cliente - Admin
#     * Cliente - Electrónico
#     * EcoEnergy - Admin
# - Carga la MATRIZ por rol→módulo (view/add/change/delete)
# - (Opcional) Sincroniza permisos nativos de Django para que el Admin
#   muestre/oculte modelos según lo definido en la matriz.
# ------------------------------------------------------------

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

#  Ajusta el import a la app donde definiste estos modelos
# Debes tener:
#   class Module(models.Model): code, name, icon(opc)
#   class Role(models.Model):   group = OneToOneField(Group)
#   class RoleModulePermission(models.Model):
#       role(FK Role), module(FK Module),
#       can_view/add/change/delete (bool)
from usuarios.models import Module, Role, RoleModulePermission   # <- CAMBIAR si tu app NO es "accounts"


# =========================
#   CONFIG ECOENERGY
# =========================

ROLES = [
    "Cliente - Admin",
    "Cliente - Electrónico",
    "EcoEnergy - Admin",
]

MODULES = [
    ("operacion",    "Operación"),     # dispositivos, mediciones, alertas, zonas
    ("catalogo",     "Catálogo"),      # productos, categorías
    ("organizacion", "Organización"),  # organizaciones, perfiles/usuarios org
]

# Matriz por rol → módulo. Usa "all" o tupla de acciones.
# Acciones válidas: "view", "add", "change", "delete"
MATRIX = {
    # Cliente Admin: gestiona todo (dentro de SU organización; el aislamiento es aparte)
    "Cliente - Admin": {
        "operacion": "all",
        "catalogo": "all",
        "organizacion": "all",
    },
    # Cliente Electrónico: ver dispositivos/mediciones; SIN borrar
    # (si quieres permitir crear mediciones sin abrir todo, usa EXTRA_NATIVE_PERMS abajo)
    "Cliente - Electrónico": {
        "operacion": ("view",),   # base: solo ver
    },
    # EcoEnergy Admin: ve catálogo y organización a nivel global
    "EcoEnergy - Admin": {
        "catalogo": "all",
        "organizacion": "all",
        # "operacion": "all",  # agrega si deben ver también operación global
    },
}

# Si True, asigna permisos nativos (add/change/delete/view) a los Groups
# para que el Admin refleje la matriz (visibilidad/acciones).
SYNC_NATIVE_DJANGO_PERMS = True

# Mapea módulo → app_label + modelos (en minúsculas) para el sync con Admin.
# AJUSTA ESTO a tus apps y modelos reales.
APP_MODEL_MAP = {
    "operacion": {
        "app_label": "devices",                         # ej: app "devices"
        "models": ["device", "measurement", "alert", "zone"],
    },
    "catalogo": {
        "app_label": "catalog",                         # ej: app "catalog"
        "models": ["product", "category"],
    },
    "organizacion": {
        "app_label": "accounts",                        # ej: app "accounts"
        "models": ["organization", "userprofile"],      # o "membership" si aplica
    },
}

# Permisos nativos extra por rol: (app_label, codename exacto)
# Útil para granularidad fina (p.ej., permitir add_measurement a Cliente - Electrónico)
EXTRA_NATIVE_PERMS = {
    "Cliente - Electrónico": [
        ("devices", "add_measurement"),
        # ("devices", "change_measurement"),  # descomenta si quieres editar mediciones
    ],
    # "Cliente - Admin": [],      # no necesario si tiene "all"
    # "EcoEnergy - Admin": [],    # idem
}


# =========================
#   UTILIDADES
# =========================

def _as_tuple(actions):
    if actions == "all":
        return {"view", "add", "change", "delete"}
    return set(actions)

def _model_perms(app_label, model, actions=("view", "add", "change", "delete")):
    try:
        ct = ContentType.objects.get(app_label=app_label, model=model)
    except ContentType.DoesNotExist:
        return Permission.objects.none()
    codenames = [f"{act}_{model}" for act in actions]
    return Permission.objects.filter(content_type=ct, codename__in=codenames)

def _sync_native_perms_for_role(group: Group, module_code: str, actions):
    """Asigna permisos nativos del Admin según APP_MODEL_MAP y acciones."""
    if module_code not in APP_MODEL_MAP:
        return
    acts = _as_tuple(actions)
    app_label = APP_MODEL_MAP[module_code]["app_label"]
    models = APP_MODEL_MAP[module_code]["models"]

    perms = Permission.objects.none()
    for m in models:
        perms |= _model_perms(app_label, m, actions=acts)

    if perms.exists():
        group.permissions.add(*perms)

def _apply_extra_perms(group: Group, pairs):
    """Asigna codenames sueltos (granularidad fina)."""
    for app_label, codename in pairs:
        try:
            p = Permission.objects.get(content_type__app_label=app_label, codename=codename)
            group.permissions.add(p)
        except Permission.DoesNotExist:
            # Silencioso: el permiso/codename no existe (modelo no registrado o typo)
            continue


# =========================
#   COMANDO
# =========================

class Command(BaseCommand):
    help = "Siembra roles/módulos/matriz para EcoEnergy y sincroniza permisos nativos para Admin."

    @transaction.atomic
    def handle(self, *args, **options):
        # 1) Módulos
        modules = {}
        for code, name in MODULES:
            m, _ = Module.objects.get_or_create(code=code, defaults={"name": name})
            if m.name != name:
                m.name = name
                m.save(update_fields=["name"])
            modules[code] = m

        # 2) Roles (Group + Role 1:1)
        groups_roles = {}
        for rname in ROLES:
            g, _ = Group.objects.get_or_create(name=rname)
            role, _ = Role.objects.get_or_create(group=g)
            groups_roles[rname] = (g, role)

        # 3) Aplicar matriz + sincronizar permisos nativos (Admin)
        for rname, modmap in MATRIX.items():
            if rname not in groups_roles:
                continue
            group, role = groups_roles[rname]

            # Si vamos a resincronizar, limpiamos permisos nativos del Group
            if SYNC_NATIVE_DJANGO_PERMS:
                group.permissions.clear()

            for mcode, actions in modmap.items():
                if mcode not in modules:
                    continue

                acts = _as_tuple(actions)
                # Booleans en matriz (nuestra tabla)
                RoleModulePermission.objects.update_or_create(
                    role=role, module=modules[mcode],
                    defaults={
                        "can_view":   "view" in acts,
                        "can_add":    "add" in acts,
                        "can_change": "change" in acts,
                        "can_delete": "delete" in acts,
                    }
                )
                # Permisos nativos para Admin
                if SYNC_NATIVE_DJANGO_PERMS:
                    _sync_native_perms_for_role(group, mcode, actions)

            # Asignar permisos nativos extra (granularidad fina)
            if SYNC_NATIVE_DJANGO_PERMS and rname in EXTRA_NATIVE_PERMS:
                _apply_extra_perms(group, EXTRA_NATIVE_PERMS[rname])

        self.stdout.write(self.style.SUCCESS("EcoEnergy: roles, módulos y matriz listos"))
        if SYNC_NATIVE_DJANGO_PERMS:
            self.stdout.write(self.style.SUCCESS("Permisos nativos sincronizados para el Admin"))
        else:
            self.stdout.write(self.style.WARNING("¡ SYNC_NATIVE_DJANGO_PERMS = False (no se asignaron permisos nativos)"))
