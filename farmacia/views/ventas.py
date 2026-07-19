import json




import uuid




from decimal import Decimal




from django.shortcuts import render, redirect, get_object_or_404




from django.contrib.auth.decorators import login_required




from django.contrib import messages




from django.utils import timezone




from django.http import JsonResponse, HttpResponse




from django.conf import settings









from farmacia.models import Producto, Venta, DetalleVenta, Empleado, Auditoria, MovimientoStock




from farmacia.forms import VentaForm




import qrcode




import base64
from io import BytesIO




from base64 import b64encode














def _ip(request):




    xf = request.META.get("HTTP_X_FORWARDED_FOR")




    return xf.split(",")[0].strip() if xf else request.META.get("REMOTE_ADDR")














def _carrito(request):




    return request.session.get("carrito", [])




def _guardar_carrito(request, items):
    request.session["carrito"] = items


    request.session.modified = True


def _guardar_cliente(venta):
    from farmacia.models import Cliente
    nombre = (venta.cliente_nombre or "").strip()
    email = (venta.cliente_email or "").strip()
    telefono = (venta.cliente_telefono or "").strip()
    if not nombre or (not email and not telefono):
        return
    cl = None
    if email:
        cl = Cliente.objects.filter(email__iexact=email).first()
    if not cl and telefono:
        cl = Cliente.objects.filter(telefono=telefono).first()
    if cl:
        if not cl.nombre and nombre:
            cl.nombre = nombre
        cl.puntos += int(round(float(venta.total)))
        cl.save()
    else:
        cl = Cliente.objects.create(nombre=nombre, email=email, telefono=telefono)
        cl.puntos += int(round(float(venta.total)))
        cl.save()






@login_required




def venta_nueva(request):




    productos = Producto.objects.filter(activo=True).order_by("nombre")




    carrito = _carrito(request)




    total = sum(Decimal(str(i["subtotal"])) for i in carrito)




    if request.method == "POST":




        form = VentaForm(request.POST)




        if form.is_valid() and carrito:




            venta = form.save(commit=False)




            venta.codigo = "V" + timezone.now().strftime("%Y%m%d%H%M%S")




            venta.total = total




            entregado = form.cleaned_data.get("entregado") or 0




            venta.entregado = entregado




            venta.cambio = max(Decimal("0"), Decimal(str(entregado)) - total)




            try:




                venta.empleado = Empleado.objects.get(usuario=request.user)




            except Empleado.DoesNotExist:




                venta.empleado = None




            venta.ip = _ip(request)




            venta.save()




            for i in carrito:




                p = Producto.objects.get(pk=i["id"])




                cant = int(i["cantidad"])




                if p.stock_actual < cant:




                    messages.error(request, "Stock insuficiente para " + p.nombre)




                    return redirect("venta_nueva")




                DetalleVenta.objects.create(




                    venta=venta, producto=p, codigo=p.codigo, nombre=p.nombre,




                    cantidad=cant, precio_unitario=i["precio"], subtotal=i["subtotal"])




                p.stock_actual -= cant




                p.save()




                MovimientoStock.objects.create(




                    producto=p, tipo="SALIDA", cantidad=cant,




                    stock_resultante=p.stock_actual, motivo="Venta " + venta.codigo,




                    usuario=request.user, ip=_ip(request))




            _guardar_cliente(venta)

            Auditoria.objects.create(accion="CREATE", modelo="Venta",




                objeto_id=str(venta.id), descripcion="Venta " + venta.codigo + " total " + str(total) + " EUR",




                usuario=request.user, ip=_ip(request))




            _guardar_carrito(request, [])




            try:
                from farmacia.notificaciones import crear_recordatorios_venta, enviar_recordatorio
                from django.utils import timezone as _tz
                crear_recordatorios_venta(venta)
                if venta.cliente_email:
                    for r in Recordatorio.objects.filter(cliente_email=venta.cliente_email, enviado=False):
                        if enviar_recordatorio(r):
                            r.enviado = True
                            r.fecha_envio = _tz.now()
                            r.save()
            except Exception:
                pass

            return redirect("venta_ticket", pk=venta.id)




        elif not carrito:




            messages.error(request, "El carrito esta vacio.")




    else:




        form = VentaForm()




    return render(request, "farmacia/venta_nueva.html",




                  {"form": form, "productos": productos, "carrito": carrito, "total": total})














@login_required




def venta_agregar(request):




    if request.method == "POST":




        pid = request.POST.get("producto")




        cant = int(request.POST.get("cantidad", 1))




        p = get_object_or_404(Producto, pk=pid)




        items = _carrito(request)




        for it in items:




            if it["id"] == str(p.id):




                it["cantidad"] += cant




                it["subtotal"] = float(Decimal(str(it["precio"])) * it["cantidad"])




                break




        else:




            items.append({"id": str(p.id), "nombre": p.nombre, "cantidad": cant,




                          "precio": float(p.precio_venta), "subtotal": float(p.precio_venta * cant)})




        _guardar_carrito(request, items)




        if request.headers.get("x-requested-with") == "XMLHttpRequest":




            return JsonResponse({"ok": True, "total": sum(i["subtotal"] for i in items)})




    return redirect("venta_nueva")














@login_required




def venta_quitar(request, pid):




    items = [i for i in _carrito(request) if i["id"] != str(pid)]




    _guardar_carrito(request, items)




    return redirect("venta_nueva")














@login_required




def venta_list(request):




    ventas = Venta.objects.select_related("empleado").all()[:100]




    return render(request, "farmacia/venta_list.html", {"ventas": ventas})














@login_required




def venta_ticket(request, pk):




    venta = get_object_or_404(Venta, pk=pk)




    detalles = venta.detalles.all()




    qr = generar_qr(venta)

    detalles_qr = []
    for d in detalles:
        qr_p = qrs_producto.get(d.id)
        detalles_qr.append((d, qr_p))
        if d.producto and d.producto.cn:
            try:
                link = "https://cima.aemps.es/cima/publico/html/nomenclator.html?nregistro=" + d.producto.cn
                qimg = qrcode.make(link)
                b = BytesIO(); qimg.save(b, format="PNG"); b.seek(0)
                qrs_producto[d.id] = "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
            except Exception:
                pass




    return render(request, "farmacia/venta_ticket.html",




                  {"venta": venta, "detalles": detalles, "detalles_qr": detalles_qr, "qr": qr})














def venta_verificar(request, pk):




    venta = get_object_or_404(Venta, pk=pk)




    return render(request, "farmacia/venta_verificar.html", {"venta": venta})














def generar_qr(venta):




    url = settings.SITE_URL + "/ticket/verificar/" + str(venta.id) + "/" if hasattr(settings, "SITE_URL") else "/ticket/verificar/" + str(venta.id) + "/"




    img = qrcode.make(url)




    buf = BytesIO()




    img.save(buf, format="PNG")




    return "data:image/png;base64," + b64encode(buf.getvalue()).decode()









@login_required




def venta_enviar(request, pk):




    venta = get_object_or_404(Venta, pk=pk)




    link = request.build_absolute_uri(redirect('venta_verificar', pk=venta.id).url) if False else request.build_absolute_uri('/ticket/verificar/' + str(venta.id) + '/')




    msg = 'Tu ticket de MiNuevaFarma: ' + venta.codigo + ' - Total ' + str(venta.total) + ' EUR. Verifica: ' + link




    if venta.cliente_telefono:
        from farmacia.sms import enviar_sms
        enviar_sms(venta.cliente_telefono, msg)
    if venta.cliente_email:




        try:




            from django.core.mail import send_mail




            send_mail('Tu ticket MiNuevaFarma', msg, settings.DEFAULT_FROM_EMAIL, [venta.cliente_email], fail_silently=True)




        except Exception:




            pass




    messages.success(request, 'Ticket enviado al cliente (SMS/email).')




    return redirect('venta_ticket', pk=venta.id)














def venta_ticket_pdf(request, pk):




    venta = get_object_or_404(Venta, pk=pk)




    detalles = venta.detalles.all()




    link = request.build_absolute_uri('/ticket/verificar/' + str(venta.id) + '/')




    import qrcode as _qr




    from reportlab.lib.pagesizes import A4




    from reportlab.lib.units import mm




    from reportlab.lib import colors




    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image as RLImage
    from reportlab.platypus import TableStyle




    from reportlab.lib.styles import getSampleStyleSheet




    import base64
    from io import BytesIO as _B
    buf = _B()




    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)




    ss = getSampleStyleSheet()




    elems = []




    elems.append(Paragraph('MiNuevaFarma', ss['Title']))




    elems.append(Paragraph('Ticket ' + venta.codigo + '  -  ' + venta.fecha.strftime('%d/%m/%Y %H:%M'), ss['Normal']))




    elems.append(Spacer(1, 6))




    data = [['Producto', 'Cant.', 'P.U.', 'Subtotal']]




    for d in detalles:




        data.append([d.nombre, str(d.cantidad), str(d.precio_unitario) + ' EUR', str(d.subtotal) + ' EUR'])




    data.append([", ", 'TOTAL', str(venta.total) + ' EUR'])




    t = Table(data, colWidths=[80*mm, 20*mm, 30*mm, 30*mm])




    t.setStyle(TableStyle([




        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0d6efd')),




        ('TEXTCOLOR', (0,0), (-1,0), colors.white),




        ('FONTSIZE', (0,0), (-1,-1), 9),




        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),




        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),




        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#f8f9fa')),




    ]))




    elems.append(t)




    elems.append(Spacer(1, 8))




    elems.append(Paragraph('Metodo: ' + venta.get_metodo_pago_display(), ss['Normal']))




    elems.append(Paragraph('Atendido por: ' + (str(venta.empleado) if venta.empleado else '-'), ss['Normal']))




    qr_img = _qr.make(link)




    qb = _B(); qr_img.save(qb, format='PNG'); qb.seek(0)




    elems.append(Spacer(1, 8))




    elems.append(RLImage(qb, width=40*mm, height=40*mm))




    elems.append(Paragraph('Escanea para verificar', ss['Normal']))




    doc.build(elems)




    resp = HttpResponse(buf.getvalue(), content_type='application/pdf')




    resp['Content-Disposition'] = 'attachment; filename="ticket_' + venta.codigo + '.pdf"'




    return resp

@login_required
def venta_anular(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    if request.method == "POST":
        if venta.anulada:
            messages.warning(request, "La venta ya estaba anulada.")
            return redirect("venta_list")
        motivo = request.POST.get("motivo", "Anulación manual")
        for d in venta.detalles.all():
            if d.producto:
                d.producto.stock_actual += d.cantidad
                d.producto.save()
                MovimientoStock.objects.create(
                    producto=d.producto, tipo="ENTRADA", cantidad=d.cantidad,
                    stock_resultante=d.producto.stock_actual,
                    motivo="Anulación venta " + venta.codigo, usuario=request.user, ip=_ip(request))
        venta.anulada = True
        venta.notas = (venta.notas or "") + " | ANULADA: " + motivo
        venta.save()
        Auditoria.objects.create(accion="DELETE", modelo="Venta",
                                 objeto_id=str(venta.id),
                                 descripcion="Anulación de venta " + venta.codigo + ": " + motivo,
                                 usuario=request.user, ip=_ip(request))
        messages.success(request, "Venta " + venta.codigo + " anulada. Stock revertido.")
        return redirect("venta_list")
    return render(request, "farmacia/venta_anular.html", {"venta": venta})
