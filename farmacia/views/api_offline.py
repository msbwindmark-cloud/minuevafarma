import json
import secrets
from datetime import timedelta

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from farmacia.models import Usuario, Producto, Categoria, Proveedor


def offline_app(request):
    ctx = {}
    if request.user.is_authenticated:
        user = request.user
        token = secrets.token_hex(32)
        user.token = token
        user.token_expiry = timezone.now() + timezone.timedelta(days=30)
        user.save()
        usuario = {
            "id": str(user.id),
            "username": user.username,
            "nombre": ((user.first_name + " " + user.last_name).strip()) or user.username,
            "rol": user.rol.nombre if user.rol else "",
            "is_superuser": user.is_superuser,
        }
        productos = Producto.objects.select_related("categoria", "proveedor").all()
        lista = []
        for p in productos:
            lista.append({
                "id": str(p.id),
                "codigo": p.codigo,
                "nombre": p.nombre,
                "precio_venta": float(p.precio_venta),
                "stock_actual": p.stock_actual,
                "categoria": p.categoria.nombre if p.categoria else "",
                "ubicacion": p.ubicacion,
                "foto": p.get_foto(),
                "cn": p.cn,
            })
        ctx["usuario_json"] = json.dumps(usuario)
        ctx["token_json"] = token
        ctx["productos_json"] = json.dumps(lista)
    return render(request, "farmacia/offline.html", ctx)


@csrf_exempt
def api_login(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "msg": "Metodo no permitido"}, status=405)
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"ok": False, "msg": "JSON invalido"}, status=400)
    username = data.get("username", "")
    password = data.get("password", "")
    user = authenticate(request, username=username, password=password)
    if not user:
        return JsonResponse({"ok": False, "msg": "Credenciales incorrectas"}, status=401)
    if not user.is_active:
        return JsonResponse({"ok": False, "msg": "Usuario inactivo"}, status=403)
    token = secrets.token_hex(32)
    user.token = token
    user.token_expiry = timezone.now() + timedelta(days=30)
    user.save()
    return JsonResponse({
        "ok": True,
        "token": token,
        "usuario": {
            "id": str(user.id),
            "username": user.username,
            "nombre": ((user.first_name + " " + user.last_name).strip()) or user.username,
            "rol": user.rol.nombre if user.rol else "",
            "is_superuser": user.is_superuser,
        },
    })


def api_productos(request):
    if request.method != "GET":
        return JsonResponse({"ok": False, "msg": "Metodo no permitido"}, status=405)
    q = request.GET.get("q", "").strip()
    productos = Producto.objects.select_related("categoria", "proveedor").all()
    if q:
        from django.db.models import Q
        productos = productos.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q) | Q(categoria__nombre__icontains=q))
    data = []
    for p in productos[:200]:
        data.append({
            "id": str(p.id),
            "codigo": p.codigo,
            "nombre": p.nombre,
            "precio_venta": float(p.precio_venta),
            "stock_actual": p.stock_actual,
            "categoria": p.categoria.nombre if p.categoria else "",
            "ubicacion": p.ubicacion,
            "foto": p.get_foto(),
        })
    return JsonResponse({"ok": True, "productos": data})


@login_required
def api_producto_detalle(request, pk):
    p = get_object_or_404(Producto, pk=pk)
    return JsonResponse({
        "ok": True,
        "producto": {
            "nombre": p.nombre,
            "codigo": p.codigo,
            "descripcion": p.descripcion or "",
            "categoria": p.categoria.nombre if p.categoria else "",
            "precio": float(p.precio_venta),
            "stock": p.stock_actual,
            "foto": p.get_foto(),
        }
    })
