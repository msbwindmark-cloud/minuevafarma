import os, django, random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from farmacia.models import (Cliente, Proveedor, Producto, PedidoProveedor,
                             LineaPedido, Recordatorio, Empleado)
from django.utils import timezone
from datetime import timedelta

random.seed(42)

nombres = ["Lucía García", "Miguel Torres", "Carmen Ruiz", "Javier Moreno", "Ana López",
           "David Sanz", "Elena Navarro", "Pablo Romero", "Sara Díaz", "Antonio Gil",
           "Marta Vidal", "Carlos Herrera", "Isabel Ortega", "Raúl Castro", "Patricia Núñez"]
productos = list(Producto.objects.filter(activo=True))

# 1) CLIENTES
clientes = []
for i, n in enumerate(nombres):
    c = Cliente.objects.create(
        nombre=n,
        telefono="600%03d%03d" % (i, i),
        email=("cliente%d@mail.com" % i) if i % 3 != 0 else "",
        alergias=random.choice(["", "", "Penicilina", "Sulfamidas", "Lactosa"]),
        puntos=random.choice([0, 0, 15, 30, 45, 60, 120, 200]),
    )
    clientes.append(c)
print("Clientes creados:", len(clientes))

# 2) RECORDATORIOS (a partir de clientes y productos)
meds = [p for p in productos if p.cn][:12] or productos[:12]
n = 0
for c in clientes:
    if not meds:
        break
    p = random.choice(meds)
    r = Recordatorio.objects.create(
        cliente_nombre=c.nombre, cliente_email=c.email, cliente_telefono=c.telefono,
        tipo=random.choice(['TRATAMIENTO', 'REPOSICION', 'CITA']),
        producto=p.nombre,
        mensaje="Hola %s, recuerda tu tratamiento con %s. Equipo MiNuevaFarma." % (c.nombre, p.nombre),
        enviado=random.choice([True, True, False]),
        fecha_envio=timezone.now() - timedelta(days=random.randint(0, 20)) if random.random() > 0.3 else None,
    )
    n += 1
print("Recordatorios creados:", n)

# 3) PEDIDOS sugeridos (productos con stock bajo o aleatorios) por proveedor
proveedores = list(Proveedor.objects.all())
bajos = list(Producto.objects.filter(stock_actual__lte=5, activo=True)[:8])
for prov in proveedores[:4]:
    candidatos = [p for p in bajos if (p.proveedor_id == prov.id)] or random.sample(productos, min(4, len(productos)))
    if not candidatos:
        continue
    ped = PedidoProveedor.objects.create(proveedor=prov, estado=random.choice(['SUGERIDO', 'ENVIADO', 'RECIBIDO']))
    for p in candidatos[:4]:
        LineaPedido.objects.create(pedido=ped, producto=p,
                                   cantidad_sugerida=random.randint(10, 50),
                                   cantidad_pedida=random.randint(10, 50))
    print("Pedido", ped.id, "->", ped.lineas.count(), "lineas")
print("OK")
