from django.db import models
from django.utils import timezone
import uuid


class Auditoria(models.Model):
    TIPOS = (
        ('LOGIN', 'Inicio de sesión'),
        ('LOGIN_FAIL', 'Intento de login fallido'),
        ('LOGOUT', 'Cierre de sesión'),
        ('REGISTRO', 'Registro de usuario'),
        ('2FA', 'Verificación 2FA'),
        ('CREATE', 'Creación'),
        ('UPDATE', 'Modificación'),
        ('DELETE', 'Eliminación'),
        ('VIEW', 'Consulta'),
        ('EXPORT', 'Exportación'),
        ('OTRO', 'Otro'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='auditorias')
    accion = models.CharField(max_length=15, choices=TIPOS)
    modelo = models.CharField(max_length=60, blank=True)
    objeto_id = models.CharField(max_length=60, blank=True)
    descripcion = models.TextField()
    ip = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    fecha = models.DateTimeField(default=timezone.now)
    datos = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = "Registro de auditoría"
        verbose_name_plural = "Auditoría"
        ordering = ['-fecha']
        indexes = [models.Index(fields=['-fecha']), models.Index(fields=['accion']), models.Index(fields=['usuario'])]

    def __str__(self):
        return f"[{self.fecha:%Y-%m-%d %H:%M}] {self.accion} - {self.descripcion[:50]}"
