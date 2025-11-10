
#MODELS.PY ORIGINAL DE LA UNIDAD 1
#'''
from django.db import models
from django.db.models import Q, F
from organizations.models import Organization


class BaseModel(models.Model):
    STATUS = [
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
    ]

    status = models.CharField(max_length=10, choices=STATUS, default="ACTIVE")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


# ----------------------------
# MODELS
# ---------------------------

class Category(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return self.name
    
    
class Product(BaseModel):
    """
    Catálogo de productos. Un Product puede ser "plantilla" para muchos Device.
    """
    name = models.CharField(max_length=160)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,              # PROTECT: evita borrar Category si hay Products asociados
        related_name="products",               # "category.products.all()" devuelve todos los productos de esta categoría
        help_text="Categoría del producto."
    )
    sku = models.CharField(
        max_length=80,
        unique=True,                           # evita SKU repetidos
        help_text="Código único de inventario (SKU)."
    )
    manufacturer = models.CharField(max_length=120, blank=True)
    model_name = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)

    # Especificaciones opcionales útiles para reportes o validaciones
    nominal_voltage_v = models.FloatField(null=True, blank=True)
    max_current_a = models.FloatField(null=True, blank=True)
    standby_power_w = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "product"

        # indexes: crea índices en BD para acelerar búsquedas/filtrados en estas columnas
        # Ej.: Product.objects.filter(name__icontains="fan") o sku exacto
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["sku"]),
        ]

        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"{self.name} ({self.sku})"



class AlertRule(BaseModel):
    """
    Regla de alerta (nombre + severidad + unidad).
    Puede tener umbrales por defecto, pero pueden ser sobrescritos por producto.
    """
    class Severity(models.TextChoices):
        CRITICAL = "CRITICAL", "Critical"
        HIGH     = "HIGH",     "High"
        MEDIUM   = "MEDIUM",   "Medium"
        LOW      = "LOW",      "Low"

    name = models.CharField(max_length=140)
    severity = models.CharField(
        max_length=10,
        choices=Severity.choices,
        default=Severity.MEDIUM,
        help_text="Nivel de severidad de la alerta."
    )
    unit = models.CharField(
        max_length=32,
        default="kWh",
        help_text="Unidad por defecto (kWh, W, A, etc.)."
    )

    # Umbrales por defecto (opcionales). Sirven como fallback si el producto no define override.
    default_min_threshold = models.FloatField(null=True, blank=True, help_text="Umbral mínimo por defecto.")
    default_max_threshold = models.FloatField(null=True, blank=True, help_text="Umbral máximo por defecto.")

    # Relación N:M *con datos extra* en la tabla intermedia ProductAlertRule.
    # OJO: cuando usamos through=, Django NO crea la tabla automática; usamos la nuestra.
    products = models.ManyToManyField(
        "Product",
        through="ProductAlertRule",      # ← Aquí está la “join table” explícita
        related_name="alert_rules",
        blank=True,
        help_text="Productos a los que aplica esta regla (relación N:M con umbrales por producto)."
    )

    class Meta:
        db_table = "alert_rule"
        indexes = [
            models.Index(fields=["severity"]),
            models.Index(fields=["name"]),
        ]
        constraints = [
            # Si ambos defaults existen, exigimos min <= max (en caso contrario el check pasa)
            models.CheckConstraint(
                check=Q(default_min_threshold__isnull=True) |
                      Q(default_max_threshold__isnull=True) |
                      Q(default_min_threshold__lte=F('default_max_threshold')),
                name="alert_rule_default_min_lte_max",
            )
        ]
        unique_together = [("name", "severity")]  # simple para enseñar
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} [{self.severity}]"

    # Helper: obtener el par (min, max) efectivo para un producto dado
    def effective_thresholds_for(self, product):
        """
        Retorna (min, max) usando override de ProductAlertRule si existe;
        si no, usa los defaults de la regla.
        """
        par = getattr(self, "_par_cache", None)
        if par and par.get("product_id") == product.id and par.get("alert_rule_id") == self.id:
            return par["min"], par["max"]

        link = ProductAlertRule.objects.filter(product=product, alert_rule=self).first()
        if link and link.min_threshold is not None and link.max_threshold is not None:
            # Cache sencillo para ahorrar un query si lo llaman varias veces
            self._par_cache = {
                "product_id": product.id,
                "alert_rule_id": self.id,
                "min": link.min_threshold,
                "max": link.max_threshold,
            }
            return link.min_threshold, link.max_threshold
        return self.default_min_threshold, self.default_max_threshold


class ProductAlertRule(BaseModel):
    """
    Tabla intermedia (join table) para la relación N:M entre Product y AlertRule,
    que además guarda datos adicionales: umbrales específicos por producto.

    Esto es exactamente tu idea de 'alerta_producto'.
    """
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,        # Si se borra el producto, caen sus enlaces
        related_name="product_alert_links",
        help_text="Producto al que se aplica la alerta con umbrales específicos."
    )
    alert_rule = models.ForeignKey(
        AlertRule,
        on_delete=models.CASCADE,        # Si se borra la regla, caen sus enlaces
        related_name="product_alert_links",
        help_text="Regla de alerta aplicada a este producto."
    )
    # Overrides por producto (si no quieres override, deja null y usará los defaults de AlertRule)
    min_threshold = models.FloatField(null=True, blank=True, help_text="Umbral mínimo (override).")
    max_threshold = models.FloatField(null=True, blank=True, help_text="Umbral máximo (override).")
    # Si te sirve, también puedes permitir override de unidad:
    unit_override = models.CharField(max_length=32, null=True, blank=True, help_text="Unidad específica (opcional).")

    class Meta:
        db_table = "product_alert_rule"
        # Un producto no debería tener la misma regla repetida:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "alert_rule"],
                name="uix_product_alert_unique"
            ),
            # Si ambos overrides existen, exigimos min <= max
            models.CheckConstraint(
                check=Q(min_threshold__isnull=True) |
                      Q(max_threshold__isnull=True) |
                      Q(min_threshold__lte=F('max_threshold')),
                name="par_min_lte_max",
            ),
        ]
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["alert_rule"]),
            models.Index(fields=["product", "alert_rule"]),  # útil para búsquedas directas
        ]
        ordering = ["product_id", "alert_rule_id"]

    def __str__(self):
        return f"{self.product.name} ⟷ {self.alert_rule.name}"
# ──────────────────────────────────────────────────────────────────────────────
# Datos por organización (tenant): Zone, Device, Measurement, AlertEvent
# ──────────────────────────────────────────────────────────────────────────────    

class Zone(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(
    "organizations.Organization",  # referencia en string para evitar import circular
    on_delete=models.CASCADE,
    related_name="zones"           # opcional, útil para acceder a las zonas desde Organization
)

    def __str__(self):
        return self.name


class Device(BaseModel):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    power = models.IntegerField(help_text="Power in Watts", null=True, blank=True)
    max_consumption = models.IntegerField(help_text="Maximum allowed consumption in kWh")
    image = models.ImageField(upload_to='dispositivos/', null=True, blank=True)
    stock = models.IntegerField(default=0)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.category})"


class Measurement(BaseModel):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    measured_at = models.DateTimeField(auto_now_add=True)
    value = models.FloatField(help_text="Consumption in kWh")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.device} - {self.value} kWh"


class Alert(BaseModel):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    triggered_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=50)
    message = models.TextField()
    alert_status = models.CharField(
        max_length=10,
        choices=[("PENDING", "Pending"), ("RESOLVED", "Resolved")],
        default="PENDING"
    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return f"Alert {self.type} - {self.device}"
    