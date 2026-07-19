from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import F
from django.utils import timezone
import io

from farmacia.models import Producto, Proveedor, PedidoProveedor, LineaPedido, MovimientoStock


def _ip(request):
    xf = request.META.get('HTTP_X_FORWARDED_FOR')
    return xf.split(',')[0].strip() if xf else request.META.get('REMOTE_ADDR')


@login_required
def pedido_sugerir(request):
    productos = Producto.objects.filter(stock_actual__lte=F('stock_minimo'), activo=True).select_related('proveedor')
    sugerencias = []
    for p in productos:
        sugerida = max(p.stock_minimo * 2 - p.stock_actual, p.stock_minimo)
        sugerencias.append({'producto': p, 'sugerida': sugerida,
                            'proveedor': p.proveedor.nombre if p.proveedor else 'Sin proveedor'})
    proveedores = Proveedor.objects.all()
    return render(request, 'farmacia/pedido_sugerir.html', {
        'sugerencias': sugerencias, 'proveedores': proveedores})


@login_required
def pedido_generar(request):
    if request.method == 'POST':
        proveedor_id = request.POST.get('proveedor')
        ids = request.POST.getlist('producto_id')
        cantidades = request.POST.getlist('cantidad')
        if not proveedor_id:
            messages.error(request, "Selecciona un proveedor.")
            return redirect('pedido_sugerir')
        proveedor = get_object_or_404(Proveedor, pk=proveedor_id)
        pedido = PedidoProveedor.objects.create(proveedor=proveedor, estado='SUGERIDO',
                                                 creado_por=request.user if request.user.is_authenticated else None)
        for pid, cant in zip(ids, cantidades):
            if not pid:
                continue
            try:
                p = Producto.objects.get(pk=pid)
            except Producto.DoesNotExist:
                continue
            cant = int(cant or 0)
            if cant <= 0:
                continue
            LineaPedido.objects.create(pedido=pedido, producto=p, cantidad_sugerida=cant, cantidad_pedida=cant)
        if not pedido.lineas.exists():
            pedido.delete()
            messages.warning(request, "No se incluyó ningún producto.")
            return redirect('pedido_sugerir')
        messages.success(request, "Pedido sugerido creado para %s con %d líneas." % (proveedor, pedido.lineas.count()))
        return redirect('pedido_detalle', pk=pedido.id)
    return redirect('pedido_sugerir')


@login_required
def pedido_list(request):
    pedidos = PedidoProveedor.objects.select_related('proveedor', 'creado_por').all()
    return render(request, 'farmacia/pedido_list.html', {'pedidos': pedidos})


@login_required
def pedido_detalle(request, pk):
    pedido = get_object_or_404(PedidoProveedor, pk=pk)
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'RECIBIDO':
            for l in pedido.lineas.all():
                if l.producto:
                    l.producto.stock_actual += l.cantidad_pedida
                    l.producto.save()
                    MovimientoStock.objects.create(producto=l.producto, tipo='ENTRADA',
                                                   cantidad=l.cantidad_pedida,
                                                   stock_resultante=l.producto.stock_actual,
                                                   motivo="Recepción pedido %s" % pedido.id,
                                                   usuario=request.user, ip=_ip(request))
            pedido.estado = 'RECIBIDO'
            pedido.save()
            messages.success(request, "Pedido marcado como recibido. Stock actualizado.")
            return redirect('pedido_detalle', pk=pedido.id)
        elif accion == 'ENVIADO':
            pedido.estado = 'ENVIADO'
            pedido.save()
            messages.info(request, "Pedido marcado como enviado.")
            return redirect('pedido_detalle', pk=pedido.id)
    return render(request, 'farmacia/pedido_detalle.html', {'pedido': pedido})


@login_required
def pedido_pdf(request, pk):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    pedido = get_object_or_404(PedidoProveedor, pk=pk)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=15 * mm, bottomMargin=15 * mm)
    styles = getSampleStyleSheet()
    elems = [Paragraph('<b>MiNuevaFarma - Pedido a proveedor</b>', styles['Title']), Spacer(1, 6)]
    elems.append(Paragraph('Proveedor: %s' % pedido.proveedor, styles['Normal']))
    elems.append(Paragraph('Fecha: %s &nbsp; Estado: %s' % (pedido.fecha.strftime('%d/%m/%Y %H:%M'), pedido.get_estado_display()), styles['Normal']))
    elems.append(Spacer(1, 8))
    data = [[Paragraph('<b>Producto</b>', styles['Normal']), Paragraph('<b>Cantidad</b>', styles['Normal'])]]
    for l in pedido.lineas.all():
        data.append([Paragraph(l.producto.nombre if l.producto else '-', styles['Normal']),
                     Paragraph(str(l.cantidad_pedida), styles['Normal'])])
    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f6fb')]),
    ]))
    elems.append(t)
    doc.build(elems)
    buf.seek(0)
    resp = HttpResponse(buf.getvalue(), content_type='application/pdf')
    resp['Content-Disposition'] = 'attachment; filename="pedido_%s.pdf"' % pedido.id
    return resp
