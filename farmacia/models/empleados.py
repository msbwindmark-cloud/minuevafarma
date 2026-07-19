from django.db import models
from django.utils import timezone
import uuid


class Empleado(models.Model):
    PUESTO = (
        ('FARM', 'Farmacéutico'),
        ('TEC', 'Técnico en farmacia'),
        ('CAJ', 'Cajero'),
        ('ADM', 'Administración'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField('Usuario', on_delete=models.CASCADE, related_name='empleado', null=True, blank=True)
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=150)
    dni = models.CharField(max_length=20, unique=True)
    puesto = models.CharField(max_length=4, choices=PUESTO, default='FARM')
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    fecha_alta = models.DateField(default=timezone.now)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"

    def fichado_hoy(self):
        hoy = timezone.now().date()
        return Fichaje.objects.filter(empleado=self, entrada__date=hoy, salida__isnull=True).first()


class Fichaje(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='fichajes')
    entrada = models.DateTimeField(default=timezone.now)
    salida = models.DateTimeField(blank=True, null=True)
    nota = models.CharField(max_length=160, blank=True)
    ip = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        verbose_name = "Fichaje"
        verbose_name_plural = "Fichajes"
        ordering = ['-entrada']

    def __str__(self):
        return f"{self.empleado} {self.entrada:%d/%m %H:%M}"

    def duracion(self):
        if self.salida:
            return self.salida - self.entrada
        return timezone.now() - self.entrada
