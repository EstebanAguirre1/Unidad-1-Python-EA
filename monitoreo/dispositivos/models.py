from django.db import models

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
# ----------------------------

class Organization(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Category(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Zone(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Device(BaseModel):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    power = models.IntegerField(help_text="Power in Watts", null=True, blank=True)
    max_consumption = models.IntegerField(help_text="Maximum allowed consumption in kWh")

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





