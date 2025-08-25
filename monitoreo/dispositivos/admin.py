from django.contrib import admin
from .models import Categoria, Zona, Dispositivo, Medicion, Alerta

admin.site.register(Categoria)
admin.site.register(Zona)
admin.site.register(Dispositivo)
admin.site.register(Medicion)
admin.site.register(Alerta)

