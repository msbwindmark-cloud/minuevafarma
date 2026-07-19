import random
import string
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse

from farmacia.forms import (LoginForm, TwoFactorForm, RegistroForm,
                            PasswordResetRequestForm, PasswordResetConfirmForm, PerfilForm)
from farmacia.models import Usuario, Auditoria

MAX_INTENTOS = 5
BLOQUEO_MINUTOS = 15
CODIGO_VIDA = 10


def _ip(request):
    xf = request.META.get('HTTP_X_FORWARDED_FOR')
    if xf:
        return xf.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _generar_codigo():
    return ''.join(random.choices(string.digits, k=6))


def _enviar_codigo(user, codigo):
    send_mail(
        'Código de verificación - MiNuevaFarma',
        f'Tu código de verificación es: {codigo}\nVálido durante {CODIGO_VIDA} minutos.',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )


def registro(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegistroForm(request.POST, request.FILES)
        if form.is_valid():
            perfil = request.POST.get('perfil', 'normal')
            user = form.save(commit=False)
            user.is_active = True
            user.debe_cambiar_password = False
            if perfil == 'staff':
                user.is_staff = True
            else:
                user.is_staff = False
            user.save()
            Auditoria.objects.create(
                usuario=user, accion='REGISTRO', modelo='Usuario',
                descripcion=f"Registro de nuevo usuario {user.username} (perfil: {perfil})",
                ip=_ip(request), user_agent=request.META.get('HTTP_USER_AGENT', '')[:500])
            messages.success(request, 'Registro completado. Ya puedes iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'farmacia/registro.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            ident = form.cleaned_data['identificador']
            pwd = form.cleaned_data['password']
            try:
                user = Usuario.objects.get(email__iexact=ident)
            except Usuario.DoesNotExist:
                try:
                    user = Usuario.objects.get(username__iexact=ident)
                except Usuario.DoesNotExist:
                    user = None
            if user:
                if user.esta_bloqueado():
                    messages.error(request, f"Cuenta bloqueada. Inténtalo tras {user.bloqueado_hasta:%H:%M}.")
                    Auditoria.objects.create(usuario=user, accion='LOGIN_FAIL', modelo='Auth',
                        descripcion='Login bloqueado (cuenta bloqueada)', ip=_ip(request))
                    return render(request, 'farmacia/login.html', {'form': form})
                user_obj = authenticate(request, username=user.username, password=pwd)
                if user_obj is not None:
                    if not user_obj.is_active:
                        messages.warning(request, 'Tu cuenta aún no está activada. Contacta con un administrador.')
                        return render(request, 'farmacia/login.html', {'form': form})
                    user_obj.intentos_fallidos = 0
                    user_obj.bloqueado_hasta = None
                    if user_obj.two_factor_enabled:
                        codigo = _generar_codigo()
                        user_obj.two_factor_code = codigo
                        user_obj.two_factor_expiry = timezone.now() + timedelta(minutes=CODIGO_VIDA)
                        user_obj.save()
                        _enviar_codigo(user_obj, codigo)
                        request.session['2fa_user'] = str(user_obj.id)
                        request.session['2fa_remember'] = form.cleaned_data['remember']
                        return redirect('verificar_2fa')
                    user_obj.last_login_ip = _ip(request)
                    user_obj.save()
                    login(request, user_obj)
                    return redirect('dashboard')
                else:
                    user.intentos_fallidos += 1
                    if user.intentos_fallidos >= MAX_INTENTOS:
                        user.bloqueado_hasta = timezone.now() + timedelta(minutes=BLOQUEO_MINUTOS)
                        user.intentos_fallidos = 0
                    user.save()
                    Auditoria.objects.create(usuario=user, accion='LOGIN_FAIL', modelo='Auth',
                        descripcion='Contraseña incorrecta', ip=_ip(request))
                    messages.error(request, 'Credenciales incorrectas.')
            else:
                messages.error(request, 'Credenciales incorrectas.')
        else:
            messages.error(request, 'Revisa los datos introducidos.')
    else:
        form = LoginForm()
    return render(request, 'farmacia/login.html', {'form': form})


def verificar_2fa(request):
    user_id = request.session.get('2fa_user')
    if not user_id:
        return redirect('login')
    user = get_object_or_404(Usuario, id=user_id)
    if request.method == 'POST':
        form = TwoFactorForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['code']
            if user.two_factor_code == codigo and user.two_factor_expiry and user.two_factor_expiry > timezone.now():
                user.two_factor_code = ''
                user.two_factor_expiry = None
                user.last_login_ip = _ip(request)
                user.save()
                login(request, user)
                Auditoria.objects.create(usuario=user, accion='2FA', modelo='Auth',
                    descripcion='2FA verificado correctamente', ip=_ip(request))
                return redirect('dashboard')
            else:
                messages.error(request, 'Código incorrecto o expirado.')
                Auditoria.objects.create(usuario=user, accion='LOGIN_FAIL', modelo='Auth',
                    descripcion='2FA fallido', ip=_ip(request))
    else:
        form = TwoFactorForm()
    return render(request, 'farmacia/2fa.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        Auditoria.objects.create(usuario=request.user, accion='LOGOUT', modelo='Auth',
            descripcion='Cierre de sesión', ip=_ip(request))
    logout(request)
    return redirect('login')


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = Usuario.objects.get(email__iexact=email, is_active=True)
                codigo = _generar_codigo()
                user.two_factor_code = codigo
                user.two_factor_expiry = timezone.now() + timedelta(minutes=CODIGO_VIDA)
                user.save()
                _enviar_codigo(user, codigo)
                request.session['reset_user'] = str(user.id)
                messages.success(request, 'Te hemos enviado un código de recuperación a tu email.')
                return redirect('password_reset_confirm')
            except Usuario.DoesNotExist:
                messages.success(request, 'Si el email existe, recibirás instrucciones.')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'farmacia/password_reset_request.html', {'form': form})


def password_reset_confirm(request):
    user_id = request.session.get('reset_user')
    if not user_id:
        return redirect('password_reset_request')
    user = get_object_or_404(Usuario, id=user_id)
    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        codigo = request.POST.get('codigo', '').strip()
        if form.is_valid():
            if codigo == user.two_factor_code and user.two_factor_expiry and user.two_factor_expiry > timezone.now():
                user.set_password(form.cleaned_data['password1'])
                user.two_factor_code = ''
                user.two_factor_expiry = None
                user.debe_cambiar_password = False
                user.save()
                del request.session['reset_user']
                messages.success(request, 'Contraseña actualizada. Inicia sesión.')
                return redirect('login')
            else:
                messages.error(request, 'El código ha expirado. Solicita uno nuevo.')
                return redirect('password_reset_request')
    else:
        form = PasswordResetConfirmForm()
    return render(request, 'farmacia/password_reset_confirm.html', {'form': form, 'codigo_requerido': True})


@login_required
def perfil(request):
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado.')
            return redirect('perfil')
    else:
        form = PerfilForm(instance=request.user)
    return render(request, 'farmacia/perfil.html', {'form': form})


@login_required
def toggle_2fa(request):
    if request.method == 'POST':
        user = request.user
        user.two_factor_enabled = not user.two_factor_enabled
        user.save()
        estado = 'activado' if user.two_factor_enabled else 'desactivado'
        Auditoria.objects.create(usuario=user, accion='UPDATE', modelo='Usuario',
            descripcion=f"2FA {estado}", ip=_ip(request))
        return JsonResponse({'ok': True, 'enabled': user.two_factor_enabled})
    return JsonResponse({'ok': False}, status=405)
