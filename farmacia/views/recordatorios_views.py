from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from farmacia.models import Recordatorio, Cliente
from farmacia.notificaciones import enviar_recordatorio


@login_required
def recordatorio_list(request):
    q = request.GET.get('q', '')
    qs = Recordatorio.objects.all()
    if q:
        qs = qs.filter(cliente_nombre__icontains=q) | qs.filter(cliente_email__icontains=q) | qs.filter(producto__icontains=q)
    pendientes = qs.filter(enviado=False).count()
    return render(request, 'farmacia/recordatorio_list.html', {
        'recordatorios': qs[:200], 'pendientes': pendientes, 'q': q})


@login_required
def recordatorio_reenviar(request, pk):
    r = get_object_or_404(Recordatorio, pk=pk)
    if enviar_recordatorio(r):
        r.enviado = True
        r.fecha_envio = timezone.now()
        r.save()
        messages.success(request, "Recordatorio reenviado.")
    else:
        messages.warning(request, "No se pudo enviar (sin email ni teléfono).")
    return redirect('recordatorio_list')


@login_required
def recordatorio_crear(request):
    if request.method == 'POST':
        nombre = request.POST.get('cliente_nombre', '')
        email = request.POST.get('cliente_email', '')
        telefono = request.POST.get('cliente_telefono', '')
        mensaje = request.POST.get('mensaje', '')
        producto = request.POST.get('producto', '')
        tipo = request.POST.get('tipo', 'TRATAMIENTO')
        if not (email or telefono) or not mensaje:
            messages.error(request, "Email o teléfono y mensaje son obligatorios.")
            return redirect('recordatorio_crear')
        r = Recordatorio.objects.create(cliente_nombre=nombre, cliente_email=email,
                                         cliente_telefono=telefono, mensaje=mensaje,
                                         producto=producto, tipo=tipo)
        if 'enviar' in request.POST:
            if enviar_recordatorio(r):
                r.enviado = True
                r.fecha_envio = timezone.now()
                r.save()
                messages.success(request, "Recordatorio creado y enviado.")
            else:
                messages.warning(request, "Creado pero no enviado (sin email/teléfono válido).")
        else:
            messages.success(request, "Recordatorio guardado como pendiente.")
        return redirect('recordatorio_list')
    return render(request, 'farmacia/recordatorio_form.html')


@login_required
def campana_enviar(request):
    if request.method == 'POST':
        asunto = request.POST.get('asunto', 'MiNuevaFarma')
        mensaje = request.POST.get('mensaje', '')
        canal = request.POST.get('canal', 'EMAIL')
        min_puntos = int(request.POST.get('min_puntos', 0) or 0)
        clientes = Cliente.objects.filter(puntos__gte=min_puntos)
        if canal == 'EMAIL':
            clientes = clientes.exclude(email='')
        else:
            clientes = clientes.exclude(telefono='')
        enviados = 0
        for c in clientes:
            texto = mensaje.replace('{nombre}', c.nombre)
            if canal == 'EMAIL':
                try:
                    from django.core.mail import send_mail
                    from django.conf import settings
                    send_mail(asunto, texto, settings.DEFAULT_FROM_EMAIL, [c.email], fail_silently=True)
                    enviados += 1
                except Exception:
                    pass
            else:
                try:
                    from farmacia.sms import enviar_sms
                    enviar_sms(c.telefono, texto)
                    enviados += 1
                except Exception:
                    pass
        messages.success(request, "Campaña enviada a %d cliente(s) por %s." % (enviados, canal))
        return redirect('campana_enviar')
    total = Cliente.objects.count()
    fidelizados = Cliente.objects.filter(puntos__gt=0).count()
    return render(request, 'farmacia/campana_form.html', {'total': total, 'fidelizados': fidelizados})
