from django.db import models


class Cliente(models.Model):
    nombre = models.CharField(max_length=120)
    telefono = models.CharField(max_length=20, blank=True, unique=False)
    email = models.EmailField(blank=True)
    alergias = models.TextField(blank=True, verbose_name="Alergias / observaciones")
    puntos = models.IntegerField(default=0, verbose_name="Puntos de fidelización")
    fecha_alta = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
