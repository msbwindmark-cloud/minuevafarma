from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import uuid


class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del rol")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    puede_gestionar_usuarios = models.BooleanField(default=False)
    puede_gestionar_productos = models.BooleanField(default=False)
    puede_ventas = models.BooleanField(default=False)
    puede_auditoria = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class UsuarioManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('is_active', True)
        return self.create_user(email, username, password, **extra)


class Usuario(AbstractBaseUser, PermissionsMixin):
    TIPO_DOC = (
        ('DNI', 'DNI'),
        ('NIE', 'NIE'),
        ('PASS', 'Pasaporte'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True, verbose_name="Usuario")
    email = models.EmailField(unique=True, verbose_name="Email")
    first_name = models.CharField(max_length=50, blank=True, verbose_name="Nombre")
    last_name = models.CharField(max_length=50, blank=True, verbose_name="Apellidos")
    tipo_documento = models.CharField(max_length=5, choices=TIPO_DOC, default='DNI')
    numero_documento = models.CharField(max_length=30, blank=True)
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')
    foto = models.ImageField(upload_to='usuarios/', blank=True, null=True)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    two_factor_enabled = models.BooleanField(default=False, verbose_name="2FA activado")
    two_factor_code = models.CharField(max_length=6, blank=True)
    two_factor_expiry = models.DateTimeField(blank=True, null=True)
    intentos_fallidos = models.PositiveSmallIntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(blank=True, null=True)
    debe_cambiar_password = models.BooleanField(default=False)
    token = models.CharField(max_length=64, blank=True)
    token_expiry = models.DateTimeField(blank=True, null=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['username']

    def __str__(self):
        return f"{self.username} ({self.email})"

    def esta_bloqueado(self):
        if self.bloqueado_hasta and self.bloqueado_hasta > timezone.now():
            return True
        return False

    def nombre_completo(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
