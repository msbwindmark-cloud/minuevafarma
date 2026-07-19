from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import F, Sum, Count
from datetime import timedelta
from farmacia.models import Auditoria, Usuario, Producto, Venta, DetalleVenta


@login_required
def dashboard(request):
    total_usuarios = Usuario.objects.count()
    ultimos_logs = Auditoria.objects.select_related('usuario').all()[:100]
    hoy = timezone.now().date()
    productos_bajo = Producto.objects.filter(stock_actual__lte=F('stock_minimo')).count()
    hoy = timezone.now().date()
    limite = hoy + timedelta(days=30)
    caducados = list(Producto.objects.filter(caducidad__lt=hoy, activo=True).order_by('caducidad')[:15])
    por_caducar = list(Producto.objects.filter(caducidad__gte=hoy, caducidad__lte=limite, activo=True).order_by('caducidad')[:15])
    stock_bajo_list = list(Producto.objects.filter(stock_actual__lte=F('stock_minimo'), activo=True).order_by('stock_actual')[:15])
    stats = {
        'usuarios': total_usuarios,
        'logins_hoy': Auditoria.objects.filter(accion='LOGIN', fecha__date=hoy).count(),
        'bloqueados': Usuario.objects.filter(bloqueado_hasta__gt=timezone.now()).count(),
        'stock_bajo': productos_bajo,
    }
    ventas = Venta.objects.filter(fecha__gte=timezone.now().date() - timedelta(days=29))
    ventas_dia = ventas.extra(select={'d': "date(fecha)"}).values('d').annotate(total=Sum('total')).order_by('d')
    dias = [(timezone.now().date() - timedelta(days=29 - i)) for i in range(30)]
    labels_dia = [d.strftime('%d/%m') for d in dias]
    totales_dia = [float(next((v['total'] for v in ventas_dia if v['d'] == d), 0) or 0) for d in dias]
    total_mes = float(ventas.aggregate(s=Sum('total'))['s'] or 0)
    num_ventas = ventas.count()
    margen = 0.0
    for dv in DetalleVenta.objects.filter(venta__in=ventas).select_related('producto'):
        coste = float(dv.producto.precio_compra) if dv.producto and dv.producto.precio_compra else 0
        margen += float(dv.precio_unitario) * dv.cantidad - coste * dv.cantidad
    por_metodo = list(ventas.values('metodo_pago').annotate(total=Sum('total'), n=Count('id')).order_by('-total'))
    labels_metodo = [m['metodo_pago'] for m in por_metodo]
    totales_metodo = [float(m['total']) for m in por_metodo]
    top = DetalleVenta.objects.filter(venta__in=ventas).values('producto__nombre').annotate(
        unidades=Sum('cantidad'), ingreso=Sum('subtotal')).order_by('-ingreso')[:6]
    labels_top = [t['producto__nombre'] for t in top]
    ingreso_top = [float(t['ingreso']) for t in top]
    graficos = {
        'labels_dia': labels_dia, 'totales_dia': totales_dia,
        'labels_metodo': labels_metodo, 'totales_metodo': totales_metodo,
        'labels_top': labels_top, 'ingreso_top': ingreso_top,
        'total_mes': total_mes, 'num_ventas': num_ventas, 'margen': round(margen, 2),
    }
    return render(request, 'farmacia/dashboard.html',
                  {'stats': stats, 'ultimos_logs': ultimos_logs, 'graficos': graficos,
                   'caducados': caducados, 'por_caducar': por_caducar, 'stock_bajo_list': stock_bajo_list})


@login_required
def auditoria_list(request):
    logs = Auditoria.objects.select_related('usuario').all()
    return render(request, 'farmacia/auditoria.html', {'logs': logs})
