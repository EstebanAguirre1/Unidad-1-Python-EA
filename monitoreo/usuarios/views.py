from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from .models import Usuario
from dispositivos.models import Organization
from django.contrib import messages
from django.views.decorators.cache import never_cache
from .forms import LoginForm, ProfileForm, CustomPasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseForbidden

def registro(request):
    if request.method == "POST":
        nombre_empresa = request.POST.get("nombre_empresa")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        # Validaciones básicas
        if not nombre_empresa or not email or not password or not password2:
            messages.error(request, "Todos los campos son obligatorios")
            return render(request, "usuarios/registro.html")

        if password != password2:
            messages.error(request, "Las contraseñas no coinciden")
            return render(request, "usuarios/registro.html")

        if User.objects.filter(username=email).exists():
            messages.error(request, "El correo ya está registrado")
            return render(request, "usuarios/registro.html")

        # Crear usuario y organización
        user = User.objects.create_user(username=email, email=email, password=password)
        org = Organization.objects.create(name=nombre_empresa)
        Usuario.objects.create(user=user, organization=org)

        messages.success(request, "Registro exitoso. Ahora inicia sesión.")
        return redirect("login")

    return render(request, "usuarios/registro.html")


@never_cache
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        # Validar campos vacíos
        if not username or not password:
            messages.error(request, "Debes completar todos los campos.")
            return redirect("login")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Bienvenido {user.username}")
            return redirect("perfil")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return redirect("login")

    return render(request, "usuarios/login.html")

@never_cache
def logout_view(request):
    # Evitar que el admin use este logout
    if request.path.startswith('/admin'):
        return HttpResponseForbidden("No autorizado para cerrar sesión del administrador.")

    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("login")


# Configuración de validación de imagen
MAX_AVATAR_SIZE_MB = 2  # Tamaño máximo 2 MB
ALLOWED_AVATAR_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']

@login_required
def perfil_view(request):
    usuario = Usuario.objects.get(user=request.user)

    if request.method == "POST":
        # Actualizar datos personales y avatar
        if "first_name" in request.POST:
            request.user.first_name = request.POST.get("first_name")
            request.user.last_name = request.POST.get("last_name")
            request.user.email = request.POST.get("email")
            usuario.telefono = request.POST.get("telefono")

            avatar_file = request.FILES.get("avatar")
            if avatar_file:
                # Validar extensión
                ext = avatar_file.name.split('.')[-1].lower()
                if ext not in ALLOWED_AVATAR_EXTENSIONS:
                    messages.error(request, f"Tipo de archivo no permitido. Usa: {', '.join(ALLOWED_AVATAR_EXTENSIONS)}")
                    return redirect("perfil")
                
                # Validar tamaño
                if avatar_file.size > MAX_AVATAR_SIZE_MB * 1024 * 1024:
                    messages.error(request, f"Archivo demasiado grande. Máximo {MAX_AVATAR_SIZE_MB} MB.")
                    return redirect("perfil")

                # Guardar avatar
                usuario.avatar = avatar_file

            request.user.save()
            usuario.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("perfil")

        # Cambiar contraseña
        elif "new_password" in request.POST:
            new_pass = request.POST.get("new_password")
            confirm_pass = request.POST.get("confirm_password")

            if new_pass != confirm_pass:
                messages.error(request, "Las contraseñas no coinciden.")
                return redirect("perfil")

            # Validaciones mínimas
            if len(new_pass) < 8 or not any(c.isupper() for c in new_pass) or not any(c.isdigit() for c in new_pass):
                messages.error(request, "La contraseña debe tener al menos 8 caracteres, una mayúscula y un número.")
                return redirect("perfil")

            request.user.set_password(new_pass)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Mantiene la sesión activa
            messages.success(request, "Contraseña cambiada correctamente.")
            return redirect("perfil")

    return render(request, "usuarios/perfil.html", {"usuario": usuario})


@login_required
def cambiar_contraseña(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Mantener sesión activa después de cambio de contraseña
            update_session_auth_hash(request, user)
            messages.success(request, "Contraseña actualizada correctamente.")
            return redirect("perfil")
        else:
            messages.error(request, "Corrige los errores en el formulario.")
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, "usuarios/cambiar_contraseña.html", {"form": form})
