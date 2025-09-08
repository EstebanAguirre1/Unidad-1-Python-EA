from django.contrib.auth.models import User
from django.db import models
from dispositivos.models import Organization

class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
