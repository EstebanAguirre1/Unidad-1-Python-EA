from django.core.management.base import BaseCommand
from dispositivos.models import Category, Product, AlertRule, ProductAlertRule

class Command(BaseCommand):
    help = "Carga catálogo en español (categorías, productos, alertas y overrides)"

    def handle(self, *args, **kwargs):
        cat_i1, _ = Category.objects.get_or_create(name="Iluminación")
        cat_c1, _ = Category.objects.get_or_create(name="Climatización")
        cat_co, _ = Category.objects.get_or_create(name="Computación")

        p1, _ = Product.objects.get_or_create(
            sku="LED-50M",
            defaults=dict(name="Panel LED 50M", category=cat_i1,
            manufacturer="Ecoluz", model_name="PL-50",
            description="Panel LED para oficinas con alta eficiencia.",
            nominal_voltage_v=220, max_current_a=0.25, standby_power_w=1.0)
        )

        # ... crea p2..p5 similar ...

        r1, _ = AlertRule.objects.get_or_create(
            name="Consumo alto", severity="HIGH", defaults=dict(unit="kwh", default_max_threshold=50.0)
        )
        r2, _ = AlertRule.objects.get_or_create(
            name="Consumo en espera elevado", severity="MEDIUM", defaults=dict(unit="kwh", default_max_threshold=0.3)
        )
        r3, _ = AlertRule.objects.get_or_create(
            name="Bajo rendimiento", severity="LOW", defaults=dict(unit="kwh", default_min_threshold=0.5)
        )

        ProductAlertRule.objects.get_or_create(product=p1, alert_rule=r1, defaults=dict(max_threshold=2.0))
        # ... el resto de overrides ...

        self.stdout.write(self.style.SUCCESS("Catálogo cargado correctamente"))