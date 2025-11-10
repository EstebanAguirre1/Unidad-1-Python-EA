from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from .forms import LoginForm

urlpatterns = [
    # --- Login ---
    path(
        'login/',
        LoginView.as_view(
            template_name="usuarios/login.html",
            authentication_form=LoginForm,
            redirect_authenticated_user=True
        ),
        name="login"
    ),

    # --- Logout personalizado ---
    path('logout/', views.logout_view, name='logout'),

    # --- Registro ---
    path('registro/', views.registro, name='registro'),

    # --- Password reset ---
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='usuarios/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='usuarios/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='usuarios/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='usuarios/password_reset_complete.html'), name='password_reset_complete'),

    # --- Perfil del usuario ---
    path('perfil/', views.perfil_view, name='perfil'),
]
