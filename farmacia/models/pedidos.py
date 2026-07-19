from django.db import models


class PedidoProveedor(models.Model):
    ESTADO = (
        ('SUGERIDO', 'Sugerido'),
        ('ENVIADO', 'Enviado'),
        ('RECIBIDO', 'Recibido'),
    )
    proveedor = models.ForeignKey('Proveedor', on_delete=models.CASCADE, related_name='pedidos')
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADO, default='SUGERIDO')
    notas = models.TextField(blank=True)
    creado_por = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Pedido a proveedor"
        verbose_name_plural = "Pedidos a proveedores"
        ordering = ['-fecha']

    def __str__(self):
        return "Pedido %s - %s (%s)" % (self.id, self.proveedor, self.get_estado_display())


class LineaPedido(models.Model):
    pedido = models.ForeignKey(PedidoProveedor, on_delete=models.CASCADE, related_name='lineas')
    producto = models.ForeignKey('Producto', on_delete=models.SET_NULL, null=True, blank=True)
    cantidad_sugerida = models.IntegerField(default=0)
    cantidad_pedida = models.IntegerField(default=0)

    def __str__(self):
        return "%s x%d" % (self.producto, self.cantidad_pedida)
