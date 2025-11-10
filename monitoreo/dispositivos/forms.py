from django import forms
from .models import Device, Category, Zone

class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = ["name", "description", "organization"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de la zona"}),
            "description": forms.Textarea(attrs={"class": "form-control", "placeholder": "Descripción (opcional)", "rows": 3}),
            "organization": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 3:
            raise forms.ValidationError("El nombre debe tener al menos 3 caracteres.")
        return name



class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = [
            'name', 'brand', 'model', 'power', 'max_consumption', 
            'image', 'stock', 'category', 'zone', 'organization'
        ]
        labels = {
            'name': 'Nombre',
            'brand': 'Marca',
            'model': 'Modelo',
            'power': 'Potencia (W)',
            'max_consumption': 'Consumo máximo (kWh)',
            'image': 'Imagen',
            'stock': 'Stock',
            'category': 'Categoría',
            'zone': 'Zona',
            'organization': 'Organización',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Para inputs normales
            if not isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs['class'] = 'form-control'
            # Para FileField (imagen)
            else:
                field.widget.attrs['class'] = 'form-control-file'