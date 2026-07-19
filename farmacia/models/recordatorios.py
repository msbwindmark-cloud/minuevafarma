from django.db import models


class Recordatorio(models.Model):
    TIPO = (
        ('TRATAMIENTO', 'Recordatorio de toma'),
        ('REPOSICION', 'Reposición de medicamento'),
        ('CITA', 'Cita / revisión'),
    )
    cliente_nombre = models.CharField(max_length=120, blank=True)
    cliente_telefono = models.CharField(max_length=20, blank=True)
    cliente_email = models.EmailField(blank=True)
    tipo = models.CharField(max_length=15, choices=TIPO, default='TRATAMIENTO')
    mensaje = models.TextField()
    producto = models.CharField(max_length=200, blank=True)
    fecha_envio = models.DateTimeField(blank=True, null=True)
    enviado = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Recordatorio"
        verbose_name_plural = "Recordatorios"
        ordering = ['-creado']

    def __str__(self):
        return f"{self.tipo} - {self.cliente_nombre or self.cliente_email}"
