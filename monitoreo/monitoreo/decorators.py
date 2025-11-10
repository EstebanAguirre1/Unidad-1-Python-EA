# /decorators.py
from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def permission_or_redirect(perm_codename, redirect_to=None, msg="No tienes permisos para esta acción."):
    def _decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            print(f"DEBUG: {request.user.username} -> {perm_codename}")  # 👈 línea nueva
            print(f"DEBUG: has_perm = {request.user.has_perm(perm_codename)}")  # 👈 línea nueva

            if not request.user.is_authenticated:
                messages.warning(request, "Debes iniciar sesión para continuar.")
                return redirect('login')

            if not request.user.has_perm(perm_codename):
                if not any(msg in m.message for m in messages.get_messages(request)):
                    messages.error(request, msg)

                if redirect_to:
                    return redirect(redirect_to)
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped
    return _decorator
