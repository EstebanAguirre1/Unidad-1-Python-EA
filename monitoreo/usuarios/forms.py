from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Usuario
import re

# -----------------------------
# LOGIN FORM
# -----------------------------
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario o email",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Usuario o email"}),
        required=True,
        error_messages={
            "required": "Debes ingresar tu usuario o correo."
        }
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Contraseña"}),
        required=True,
        error_messages={
            "required": "Debes ingresar tu contraseña."
        }
    )


# -----------------------------
# PERFIL DE USUARIO
# -----------------------------
class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Nombre", max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label="Apellido", max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="Correo", required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    telefono = forms.CharField(
        label="Teléfono", required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    avatar = forms.ImageField(
        label="Avatar", required=False
    )

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono', 'avatar']

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 2*1024*1024:  # máximo 2 MB
                raise forms.ValidationError("El avatar no puede superar los 2 MB.")
            if not avatar.content_type in ['image/jpeg', 'image/png']:
                raise forms.ValidationError("Formato no válido. Solo JPEG o PNG.")
        return avatar


# -----------------------------
# CAMBIO DE CONTRASEÑA
# -----------------------------
class CustomPasswordChangeForm(PasswordChangeForm):
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Debe tener al menos 8 caracteres, una mayúscula y un número."
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        if not re.search(r'\d', password):
            raise forms.ValidationError("La contraseña debe contener al menos un número.")
        return password
