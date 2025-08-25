from django.shortcuts import render

# Create your views here.
'''
def inicio(request):
    contexto = {"nombre": "Profe Javier"}
    productos = [
       {"nombre": "Sensor 1", "valor": 100},
       {"nombre": "Sensor 2", "valor": 200},
       {"nombre": "Sensor 3", "valor": 300}
    ]
'''

def panel_dispositivos(request):
    dispositivos = [
        {"nombre": "Sensor Temperatura", "consumo": 50},
        {"nombre": "Medidor Solar", "consumo": 120},
        {"nombre": "Sensor Movimiento", "consumo": 30},
        {"nombre": "Calefactor", "consumo": 200}
    ]

    consumo_maximo = 100
    
    
    return render(request, "dispositivos/panel.html", {
        "dispositivos": dispositivos,
        "consumo_maximo": consumo_maximo
    })