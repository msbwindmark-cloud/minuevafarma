from farmacia.models import DetalleVenta, Producto
from collections import defaultdict


def sugerir(ids_carrito):
    """Devuelve productos frecuentemente comprados junto a los del carrito."""
    if not ids_carrito:
        return []
    ids_carrito = set(ids_carrito)
    conteo = defaultdict(int)
    ventas_ids = DetalleVenta.objects.filter(producto_id__in=ids_carrito).values_list("venta_id", flat=True)
    if not ventas_ids:
        return []
    otros = DetalleVenta.objects.filter(venta_id__in=list(ventas_ids)).exclude(producto_id__in=ids_carrito)
    for d in otros.values_list("producto_id").iterator():
        conteo[d[0]] += 1
    sugeridos = sorted(conteo.items(), key=lambda x: x[1], reverse=True)[:5]
    res = []
    for pid, n in sugeridos:
        p = Producto.objects.filter(id=pid).first()
        if p and p.activo:
            res.append({"id": str(p.id), "nombre": p.nombre, "precio": float(p.precio_venta), "foto": p.get_foto(), "veces": n})
    return res
