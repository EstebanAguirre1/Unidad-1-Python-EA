from django.core.management.base import BaseCommand
from dispositivos.models import Category, Product, AlertRule, ProductAlertRule, Organization, Zone, Device

class Command(BaseCommand):
    help = "Carga catálogo en español (categorías, productos, alertas y overrides)"

    def handle(self, *args, **kwargs):
        # CATÁLOGO - 2 Categories (como pide la tarea)
        cat_i1, _ = Category.objects.get_or_create(name="Iluminación")
        cat_c1, _ = Category.objects.get_or_create(name="Climatización")
        # Eliminé Computación para cumplir con "2 Category"

        # 3 Products (como pide la tarea)
        p1, _ = Product.objects.get_or_create(
            sku="LED-50W",
            defaults=dict(
                name="Panel LED 50W", 
                category=cat_i1,
                manufacturer="Ecoluz", 
                model_name="PL-50W",
                description="Panel LED para oficinas con alta eficiencia.",
                nominal_voltage_v=220, 
                max_current_a=0.25, 
                standby_power_w=1.0
            )
        )

        p2, _ = Product.objects.get_or_create(
            sku="AC-12000BTU",
            defaults=dict(
                name="Aire Acondicionado 12000 BTU",
                category=cat_c1,
                manufacturer="ClimatePro", 
                model_name="AC-12K",
                description="Aire acondicionado split de alta eficiencia.",
                nominal_voltage_v=220,
                max_current_a=5.5,
                standby_power_w=2.5
            )
        )

        p3, _ = Product.objects.get_or_create(
            sku="LED-TUBO-60",
            defaults=dict(
                name="Tubo LED 60cm",
                category=cat_i1,
                manufacturer="Ecoluz",
                model_name="TL-60",
                description="Tubo LED para reemplazo de fluorescentes.",
                nominal_voltage_v=110,
                max_current_a=0.15,
                standby_power_w=0.5
            )
        )

        # 2 AlertRules (como pide la tarea)
        r1, _ = AlertRule.objects.get_or_create(
            name="Consumo alto", 
            severity="HIGH", 
            defaults=dict(unit="kwh", default_max_threshold=50.0)
        )
        r2, _ = AlertRule.objects.get_or_create(
            name="Consumo en espera elevado", 
            severity="MEDIUM", 
            defaults=dict(unit="kwh", default_max_threshold=0.3)
        )
        # Eliminé la tercera para cumplir con "2 AlertRule"

        # Relación Product ↔ AlertRule con umbrales distintos (como pide la tarea)
        ProductAlertRule.objects.get_or_create(
            product=p1, 
            alert_rule=r1, 
            defaults=dict(max_threshold=2.0, min_threshold=0.1)
        )
        
        ProductAlertRule.objects.get_or_create(
            product=p2, 
            alert_rule=r1, 
            defaults=dict(max_threshold=8.0, min_threshold=0.5)
        )
        
        ProductAlertRule.objects.get_or_create(
            product=p1, 
            alert_rule=r2, 
            defaults=dict(max_threshold=0.1, min_threshold=0.01)
        )

        # DEMO ORGANIZACIÓN (como pide la tarea)
        # 1 Organization
        org_demo, _ = Organization.objects.get_or_create(name="Empresa Demo SA")

        # 2 Zones
        zona_oficinas, _ = Zone.objects.get_or_create(
            name="Oficinas Principal",
            organization=org_demo,
            defaults=dict(description="Área de oficinas central")
        )
        
        zona_servidores, _ = Zone.objects.get_or_create(
            name="Sala de Servidores", 
            organization=org_demo,
            defaults=dict(description="Sala de equipos críticos")
        )

        # 3 Devices
        Device.objects.get_or_create(
            name="Panel LED Oficina 101",
            organization=org_demo,
            defaults=dict(
                category=cat_i1,
                zone=zona_oficinas,
                brand="Ecoluz",
                model="PL-50W",
                max_consumption=50,
                power=45
            )
        )
        
        Device.objects.get_or_create(
            name="AC Sala de Juntas",
            organization=org_demo,
            defaults=dict(
                category=cat_c1,
                zone=zona_oficinas, 
                brand="ClimatePro",
                model="AC-12K",
                max_consumption=1200,
                power=1100
            )
        )
        
        Device.objects.get_or_create(
            name="LED Sala Servidores",
            organization=org_demo,
            defaults=dict(
                category=cat_i1,
                zone=zona_servidores,
                brand="Ecoluz", 
                model="TL-60",
                max_consumption=25,
                power=20
            )
        )

        self.stdout.write(self.style.SUCCESS("Catálogo U2 cargado correctamente: 2 Categorías, 3 Productos, 2 AlertRules, 1 Organización, 2 Zonas, 3 Dispositivos"))