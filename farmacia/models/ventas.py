from django.db import models
from django.utils import timezone
import uuid


class Venta(models.Model):
    METODO = (
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
        ('MIXTO', 'Mixto'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=20, unique=True, blank=True)
    empleado = models.ForeignKey('Empleado', on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas')
    cliente_nombre = models.CharField(max_length=120, blank=True)
    cliente_telefono = models.CharField(max_length=20, blank=True)
    cliente_email = models.EmailField(blank=True)
    metodo_pago = models.CharField(max_length=12, choices=METODO, default='EFECTIVO')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    entregado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cambio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha = models.DateTimeField(default=timezone.now)
    notas = models.TextField(blank=True)
    ip = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha']

    def __str__(self):
        return f"Venta {self.codigo} ({self.fecha:%d/%m/%Y %H:%M})"

    def detalles_count(self):
        return self.detalles.count()


class DetalleVenta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('Producto', on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas_detalle')
    codigo = models.CharField(max_length=40, blank=True)
    nombre = models.CharField(max_length=150)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Detalle de venta"
        verbose_name_plural = "Detalles de venta"

    def __str__(self):
        return f"{self.cantidad} x {self.nombre}"


