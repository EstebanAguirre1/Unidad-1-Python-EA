from django.shortcuts import render
from .models import Device

def device_panel(request):
    devices = Device.objects.select_related("category")
    return render(request, "dispositivos/panel.html", {"devices": devices})

def device_detalle(request, device_id):
    device = Device.objects.get(id=device_id)
    return render(request, "dispositivos/detalle.html", {"device": device})


