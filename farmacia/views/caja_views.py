from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from farmacia.models import Venta, Caja


@login_required
def caja_view(request):
    hoy = timezone.now().date()
    ventas = Venta.objects.filter(fecha__date=hoy, anulada=False)
    efectivo = float(ventas.filter(metodo_pago='EFECTIVO').aggregate(s=Sum('total'))['s'] or 0)
    tarjeta = float(ventas.filter(metodo_pago='TARJETA').aggregate(s=Sum('total'))['s'] or 0)
    mixto = float(ventas.filter(metodo_pago='MIXTO').aggregate(s=Sum('total'))['s'] or 0)
    total = efectivo + tarjeta + mixto
    fondo = 0
    apertura = Caja.objects.filter(tipo='APERTURA', fecha__date=hoy).order_by('-fecha').first()
    if apertura:
        fondo = float(apertura.fondo_inicial)
    esperado = fondo + efectivo
    ultimos = Caja.objects.all()[:10]
    if request.method == "POST":
        Caja.objects.create(
            tipo='CIERRE', fondo_inicial=fondo, efectivo=efectivo, tarjeta=tarjeta, total=total,
            usuario=request.user if request.user.is_authenticated else None,
            notas=request.POST.get('notas', ''))
        from django.contrib import messages
        messages.success(request, "Caja cerrada. Total del día: %.2f EUR (efectivo esperado con fondo: %.2f)" % (total, esperado))
        return redirect('caja')
    return render(request, 'farmacia/caja.html', {
        'efectivo': efectivo, 'tarjeta': tarjeta, 'mixto': mixto, 'total': total,
        'fondo': fondo, 'esperado': esperado, 'apertura': apertura is not None,
        'num': ventas.count(), 'ultimos': ultimos})


@login_required
def caja_abrir(request):
    if request.method == "POST":
        from django.contrib import messages
        from django.db.models import Sum
        fondo = float(request.POST.get('fondo_inicial') or 0)
        Caja.objects.create(
            tipo='APERTURA', fondo_inicial=fondo,
            usuario=request.user if request.user.is_authenticated else None,
            notas=request.POST.get('notas', 'Apertura de caja'))
        messages.success(request, "Caja abierta con fondo inicial de %.2f EUR." % fondo)
        return redirect('caja')
    return redirect('caja')
