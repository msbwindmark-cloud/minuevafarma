from django.db import models
from django.utils import timezone
import uuid


class Categoria(models.Model):
    nombre = models.CharField(max_length=80, unique=True, verbose_name="Categoría")
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    nombre = models.CharField(max_length=120, verbose_name="Proveedor")
    cif = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    UNIDAD = (
        ('U', 'Unidad'),
        ('C', 'Caja'),
        ('B', 'Blister'),
        ('G', 'Gramos'),
        ('ML', 'Mililitros'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=40, unique=True, verbose_name="Código/Nacional")
    cn = models.CharField(max_length=20, blank=True, verbose_name="Código Nacional (CIMA)")
    nombre = models.CharField(max_length=150, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    unidad = models.CharField(max_length=3, choices=UNIDAD, default='U')
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_actual = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=0, verbose_name="Stock mínimo (alerta)")
    ubicacion = models.CharField(max_length=30, blank=True, verbose_name="Ubicación estantería (p.ej. A3)")
    caducidad = models.DateField(blank=True, null=True)
    foto = models.ImageField(upload_to='productos/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    def stock_bajo(self):
        return self.stock_actual <= self.stock_minimo

    def caducado(self):
        return self.caducidad and self.caducidad < timezone.now().date()


class MovimientoStock(models.Model):
    TIPOS = (
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('AJUSTE', 'Ajuste'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPOS)
    cantidad = models.IntegerField()
    stock_resultante = models.IntegerField()
    motivo = models.CharField(max_length=160, blank=True)
    usuario = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(default=timezone.now)
    ip = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        verbose_name = "Movimiento de stock"
        verbose_name_plural = "Movimientos de stock"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.tipo} {self.cantidad} x {self.producto}"
