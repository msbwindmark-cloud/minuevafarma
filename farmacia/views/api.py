import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.conf import settings
from decimal import Decimal
from farmacia.models import Producto, Venta, DetalleVenta, Empleado, Auditoria, MovimientoStock


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

