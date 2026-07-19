import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.conf import settings
from decimal import Decimal
from farmacia.models import Producto, Venta, DetalleVenta, Empleado, Auditoria, MovimientoStock
from farmacia.interacciones import chequear
from farmacia.sugerencias import sugerir
from farmacia.models import Cliente, Venta, DetalleVenta, Recordatorio
from farmacia.notificaciones import crear_recordatorios_venta, enviar_recordatorio


def _enviar_notificaciones(venta, request):
    link = request.build_absolute_uri("/ticket/verificar/" + str(venta.id) + "/")
    msg = "Tu ticket de MiNuevaFarma: " + venta.codigo + " - Total " + str(venta.total) + " EUR. Verifica: " + link
    if venta.cliente_telefono:
        try:
            from farmacia.sms import enviar_sms
            enviar_sms(venta.cliente_telefono, msg)
        except Exception:
            pass
    if venta.cliente_email:
        try:
            from django.core.mail import send_mail
            send_mail("Tu ticket MiNuevaFarma", msg, settings.DEFAULT_FROM_EMAIL, [venta.cliente_email], fail_silently=True)
        except Exception:
            pass


def _procesar(carrito, data, request):
    if not carrito:
        return None
    usuario = request.user if request.user.is_authenticated else None
    import random
    codigo = "V" + timezone.now().strftime("%Y%m%d%H%M%S%f") + "O" + str(random.randint(100, 999))
    total = Decimal(str(data.get("total", 0)))
    entregado = Decimal(str(data.get("entregado", 0)))
    venta = Venta.objects.create(
        codigo=codigo, cliente_nombre=data.get("cliente_nombre", ""),
        cliente_telefono=data.get("cliente_telefono", ""), cliente_email=data.get("cliente_email", ""),
        metodo_pago=data.get("metodo_pago", "EFECTIVO"), total=total,
        entregado=entregado, cambio=max(Decimal("0"), entregado - total),
        ip=request.META.get("REMOTE_ADDR"))
    try:
        if usuario:
            venta.empleado = Empleado.objects.get(usuario=usuario)
            venta.save()
    except Exception:
        pass
    for i in carrito:
        try:
            p = Producto.objects.get(pk=i["id"])
        except Producto.DoesNotExist:
            raise ValueError("Producto no encontrado: " + str(i.get("id")))
        cant = int(i["cantidad"])
        DetalleVenta.objects.create(venta=venta, producto=p, codigo=p.codigo, nombre=p.nombre,
                                    cantidad=cant, precio_unitario=i["precio"], subtotal=i["subtotal"])
        p.stock_actual -= cant
        p.save()
        MovimientoStock.objects.create(producto=p, tipo="SALIDA", cantidad=cant,
                                      stock_resultante=p.stock_actual, motivo="Venta offline " + codigo, usuario=usuario)
    Auditoria.objects.create(accion="CREATE", modelo="Venta", objeto_id=str(venta.id),
                            descripcion="Venta offline " + codigo + " total " + str(total), usuario=usuario)
    try:
        crear_recordatorios_venta(venta)
        for r in Recordatorio.objects.filter(cliente_email=venta.cliente_email, enviado=False) if venta.cliente_email else []:
            if enviar_recordatorio(r):
                r.enviado = True
                from django.utils import timezone as _tz
                r.fecha_envio = _tz.now()
                r.save()
    except Exception:
        pass
    try:
        _enviar_notificaciones(venta, request)
    except Exception as e:
        import traceback
        traceback.print_exc()
    return codigo


@csrf_exempt
def venta_offline(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "msg": "Metodo no permitido"}, status=405)
    if request.content_type and "application/json" in request.content_type:
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({"ok": False, "msg": "JSON invalido"}, status=400)
        carrito = data.get("carrito", [])
    else:
        data = request.POST
        carrito = json.loads(data.get("carrito", "[]"))
    try:
        codigo = _procesar(carrito, data, request)
    except ValueError as e:
        return JsonResponse({"ok": False, "msg": str(e)}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"ok": False, "msg": "Error servidor: " + str(e)}, status=400)
    if not codigo:
        return JsonResponse({"ok": False, "msg": "Carrito vacio"}, status=400)
    return JsonResponse({"ok": True, "codigo": codigo})


@login_required
def chequear_interacciones_carrito(request):
    items = request.session.get("carrito", [])
    ids = [i["id"] for i in items]
    cns = list(Producto.objects.filter(id__in=ids).exclude(cn="").values_list("cn", flat=True))
    res = chequear(cns)
    nombres = {p.cn: p.nombre for p in Producto.objects.filter(cn__in=cns)}
    for r in res:
        r["nombre_a"] = nombres.get(r["a"], r["a"])
        r["nombre_b"] = nombres.get(r["b"], r["b"])
    return JsonResponse({"ok": True, "interacciones": res})


@login_required
def chequear_interacciones(request):
    if not cns:
        ids = request.GET.getlist("id")
        cns = list(Producto.objects.filter(id__in=ids).exclude(cn="").values_list("cn", flat=True))
    res = chequear(cns)
    nombres = {p.cn: p.nombre for p in Producto.objects.filter(cn__in=cns)}
    for r in res:
        r["nombre_a"] = nombres.get(r["a"], r["a"])
        r["nombre_b"] = nombres.get(r["b"], r["b"])
    return JsonResponse({"ok": True, "interacciones": res})


@login_required
def sugerencias_api(request):
    ids = request.GET.getlist("id")
    if not ids:
        ids = [i["id"] for i in request.session.get("carrito", [])]
    sug = sugerir([str(x) for x in ids])
    return JsonResponse({"ok": True, "sugerencias": sug})


@login_required
def historia_cliente(request):
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse({"ok": True, "encontrado": False})
    cliente = Cliente.objects.filter(email__iexact=q).first() or Cliente.objects.filter(telefono=q).first()
    if not cliente:
        return JsonResponse({"ok": True, "encontrado": False})
    ventas = Venta.objects.filter(cliente_email__iexact=cliente.email).order_by("-fecha")[:10]
    compras = []
    for v in ventas:
        prods = [d.nombre for d in v.detalles.all()[:6]]
        compras.append({"fecha": v.fecha.strftime("%d/%m/%Y %H:%M"), "total": float(v.total), "productos": prods})
    return JsonResponse({"ok": True, "encontrado": True, "cliente": {"nombre": cliente.nombre, "alergias": cliente.alergias, "puntos": cliente.puntos}, "compras": compras})

