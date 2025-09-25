from django.contrib.auth.models import User
from django.db import models
from dispositivos.models import Organization
from django.conf import settings

class Usuario(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.user.username} @ {self.organization.name}"
