from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Usuario
from dispositivos.models import Organization
from django.contrib import messages
from django.views.decorators.cache import never_cache

def registro(request):
    if request.method == "POST":
        nombre_empresa = request.POST.get("nombre_empresa")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if not nombre_empresa or not email or not password or not password2:
            messages.error(request, "Todos los campos son obligatorios")
            return render(request, "usuarios/registro.html")  # <-- render en vez de redirect

        if password != password2:
            messages.error(request, "Las contraseñas no coinciden")
            return render(request, "usuarios/registro.html")

        if User.objects.filter(username=email).exists():
            messages.error(request, "El correo ya está registrado")
            return render(request, "usuarios/registro.html")

        # Crear User
        user = User.objects.create_user(username=email, email=email, password=password)
        org = Organization.objects.create(name=nombre_empresa)
        Usuario.objects.create(user=user, organization=org)

        messages.success(request, "Registro exitoso, ahora inicia sesión")
        return redirect("login")

    return render(request, "usuarios/registro.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("/")  # dashboard
        else:
            messages.error(request, "Credenciales inválidas")

    return render(request, "usuarios/login.html")


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")
    return render(request, "usuarios/logout.html")


@never_cache
def cerrar_sesion(request):
    logout(request)
    return redirect('login')
