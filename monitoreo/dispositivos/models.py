from django.db import models

class BaseModel(models.Model):
    ESTADOS = [
        ("ACTIVO", "Activo"),
        ("INACTIVO", "Inactivo"),
    ]

    estado = models.CharField(max_length=10, choices=ESTADOS, default="ACTIVO")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

# ----------------------------
# MODELOS
# ----------------------------

class Categoria(BaseModel):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Zona(BaseModel):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Dispositivo(BaseModel):
    nombre = models.CharField(max_length=100)
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    potencia = models.IntegerField(help_text="Potencia en Watts", null=True, blank=True)
    consumo_maximo = models.IntegerField(help_text="Consumo máximo permitido en kWh")
    
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} ({self.categoria})"


class Medicion(BaseModel):
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    consumo = models.FloatField(help_text="Consumo en kWh")

    def __str__(self):
        return f"{self.dispositivo} - {self.consumo} kWh"


class Alerta(BaseModel):
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    tipo_alerta = models.CharField(max_length=50)
    mensaje = models.TextField()
    estado_alerta = models.CharField(
        max_length=10,
        choices=[("PENDIENTE", "Pendiente"), ("RESUELTA", "Resuelta")],
        default="PENDIENTE"
    )

    def __str__(self):
        return f"Alerta {self.tipo_alerta} - {self.dispositivo}"
