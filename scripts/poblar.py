import os, django, random, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from datetime import timedelta, date, datetime
from decimal import Decimal
from django.utils import timezone
from farmacia.models import (Categoria, Proveedor, Producto, Empleado, Fichaje,
                             Venta, DetalleVenta, MovimientoStock, Auditoria, Usuario, Rol)
from farmacia.cima import buscar_por_nombre

random.seed(42)

# ---------- CATEGORIAS ----------
cats = ['Antibioticos','Analgesicos','Antihistaminicos','Dermatologicos','Vitaminas',
        'Infantil','Cardiovascular','Digestivo','Respiratorio','Oftalmologico']
cat_objs = {}
for c in cats:
    obj, _ = Categoria.objects.get_or_create(nombre=c)
    cat_objs[c] = obj
print('Categorias:', len(cat_objs))

# ---------- PROVEEDORES ----------
provs = ['Cofares','Hefame','Bossfarma','UGU','FARMANOL']
prov_objs = {}
for p in provs:
    obj, _ = Proveedor.objects.get_or_create(nombre=p)
    prov_objs[p] = obj
print('Proveedores:', len(prov_objs))

# ---------- PRODUCTOS (farmacos reales desde CIMA) ----------
medicamentos = [
    ('Amoxicilina', 'Antibioticos'), ('Ibuprofeno', 'Analgesicos'), ('Paracetamol', 'Analgesicos'),
    ('Aspirina', 'Analgesicos'), ('Loratadina', 'Antihistaminicos'), ('Omeprazol', 'Digestivo'),
    ('Salbutamol', 'Respiratorio'), ('Metformina', 'Cardiovascular'), ('Atorvastatina', 'Cardiovascular'),
    ('Losartan', 'Cardiovascular'), ('Cetirizina', 'Antihistaminicos'), ('Dexametasona', 'Respiratorio'),
    ('Azitromicina', 'Antibioticos'), ('Diclofenaco', 'Analgesicos'), ('Pantoprazol', 'Digestivo'),
    ('Warfarina', 'Cardiovascular'), ('Enalapril', 'Cardiovascular'), ('Furosemida', 'Cardiovascular'),
    ('Clortalidona', 'Cardiovascular'), ('Levotiroxina', 'Cardiovascular'), ('Vitamina D', 'Vitaminas'),
    ('Vitamina C', 'Vitaminas'), ('Omega 3', 'Vitaminas'), ('Magnesio', 'Vitaminas'),
    ('Lactobacillus', 'Digestivo'), ('Clorhexidina', 'Dermatologicos'), ('Betametasona', 'Dermatologicos'),
    ('Furoato de mometasona', 'Respiratorio'), ('Latanoprost', 'Oftalmologico'),
    ('Tobramicina', 'Oftalmologico'), ('Tetrizolina', 'Oftalmologico'), ('Dextrometorfano', 'Respiratorio'),
    ('Ambroxol', 'Respiratorio'), ('Aciclovir', 'Antiviral'), ('Clobetasol', 'Dermatologicos'),
]

n = 0
for nombre, cat in medicamentos:
    try:
        res = buscar_por_nombre(nombre, 1)
    except Exception:
        res = []
    cima = res[0] if res else None
    cn = str(cima.get('nregistro')) if cima else ''
    nom = cima.get('nombre')[:140] if cima else (nombre + ' (generico)')
    cod = 'CN' + (cn if cn else str(1000 + n))
    if Producto.objects.filter(codigo=cod).exists():
        continue
    p = Producto.objects.create(
        codigo=cod, cn=cn, nombre=nom,
        categoria=cat_objs.get(cat), proveedor=random.choice(list(prov_objs.values())),
        unidad='U', precio_compra=Decimal(str(round(random.uniform(0.5, 8), 2))),
        precio_venta=Decimal(str(round(random.uniform(1.5, 15), 2))),
        stock_actual=random.randint(0, 80), stock_minimo=random.randint(5, 15),
        ubicacion=random.choice(['A1','A2','A3','B1','B2','C1','C2','C3','D1']),
        caducidad=date.today() + timedelta(days=random.randint(-20, 400)),
    )
    n += 1
print('Productos creados:', n)

# --------- EMPLEADOS + USUARIOS ----------
empleados_data = [
    ('Ana','Garcia','FARM'), ('Luis','Martinez','TEC'), ('Carmen','Lopez','CAJ'),
    ('Javier','Ruiz','FARM'), ('Sofia','Diaz','ADM'), ('Pablo','Sanchez','TEC'),
    ('Lucia','Fernandez','CAJ'), ('Diego','Perez','FARM'),
]
rol, _ = Rol.objects.get_or_create(nombre='Farmaceutico')
for i,(nom, ape, puesto) in enumerate(empleados_data, 1):
    dni = 'DNI%08d' % i
    if Empleado.objects.filter(dni=dni).exists():
        continue
    emp = Empleado.objects.create(nombre=nom, apellidos=ape, dni=dni, puesto=puesto,
                                   telefono='600%06d' % i, email=f'{nom.lower()}.{ape.lower()}@minuevafarma.com',
                                   fecha_alta=date.today()-timedelta(days=random.randint(30,800)))
    # usuario asociado
    uname = (nom+ape).lower()[:12]
    if not Usuario.objects.filter(username=uname).exists():
        u = Usuario.objects.create_user(username=uname, email=f'{uname}@mf.com', password='farmacia123', is_active=True)
        u.rol = rol; u.save()
        emp.usuario = u; emp.save()
    # fichajes de los ultimos 20 dias
    for d in range(20):
        base = timezone.now() - timedelta(days=d)
        if random.random() < 0.8:
            ent = base.replace(hour=random.randint(8,10), minute=random.randint(0,59))
            sal = ent + timedelta(hours=random.randint(6,9))
            Fichaje.objects.create(empleado=emp, entrada=ent, salida=sal, ip='127.0.0.1')
print('Empleados:', Empleado.objects.count())

# --------- VENTAS HISTORICAS (ultimos 60 dias) ----------
productos = list(Producto.objects.all())
clientes = ['Maria Lopez','Juan Perez','Lucia Gomez','Pedro Sanchez','Ana Ruiz',
            'Carlos Diaz','Elena Torres','Miguel Castro','Sara Moreno','David Gil']
ventas_tot = 0
for d in range(60):
    base = timezone.now() - timedelta(days=d)
    for _ in range(random.randint(3, 12)):
        hora = base.replace(hour=random.randint(9,21), minute=random.randint(0,59))
        nprod = random.randint(1, 4)
        picks = random.sample(productos, min(nprod, len(productos)))
        total = Decimal('0')
        v = Venta.objects.create(
            codigo='V%03d%02d%06d' % (d, _, random.randint(1000,9999)),
            cliente_nombre=random.choice(clientes),
            cliente_telefono='6%08d' % random.randint(10000000,99999999),
            cliente_email=random.choice(clientes).lower().replace(' ','')+'@mail.com',
            metodo_pago=random.choice(['EFECTIVO','TARJETA','TRANSFERENCIA']),
            total=Decimal('0'), entregado=Decimal('0'), cambio=Decimal('0'),
            fecha=hora, ip='127.0.0.1',
        )
        emp = random.choice(Empleado.objects.all())
        v.empleado = emp; v.save()
        for p in picks:
            cant = random.randint(1, 3)
            precio = p.precio_venta
            sub = precio * cant
            total += sub
            DetalleVenta.objects.create(venta=v, producto=p, codigo=p.codigo, nombre=p.nombre,
                                        cantidad=cant, precio_unitario=precio, subtotal=sub)
            if p.stock_actual >= cant:
                p.stock_actual -= cant; p.save()
                MovimientoStock.objects.create(producto=p, tipo='SALIDA', cantidad=cant,
                                              stock_resultante=p.stock_actual,
                                              motivo='Venta historica', usuario=emp.usuario)
        v.total = total; v.entregado = total; v.cambio = Decimal('0'); v.save()
        ventas_tot += 1
print('Ventas creadas:', ventas_tot)

# --------- AUDITORIA ----------
acciones = ['LOGIN','CREATE','UPDATE','EXPORT','VIEW']
for _ in range(50):
    u = random.choice(list(Usuario.objects.all()) + [None])
    Auditoria.objects.create(accion=random.choice(acciones), modelo=random.choice(['Venta','Producto','Empleado']),
                             descripcion='Registro automatico de prueba', usuario=u, ip='127.0.0.1')
print('Auditoria:', Auditoria.objects.count())
print('TODO OK')
