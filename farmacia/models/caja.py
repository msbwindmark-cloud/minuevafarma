from django.db import models


class Caja(models.Model):
    TIPO = (
        ('APERTURA', 'Apertura'),
        ('CIERRE', 'Cierre'),
    )
    tipo = models.CharField(max_length=10, choices=TIPO)
    fecha = models.DateTimeField(auto_now_add=True)
    fondo_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Fondo inicial")
    efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tarjeta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usuario = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    notas = models.TextField(blank=True)

    class Meta:
        verbose_name = "Movimiento de caja"
        verbose_name_plural = "Arqueo de caja"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.get_tipo_display()} {self.fecha:%d/%m/%Y %H:%M} - {self.total} EUR"
