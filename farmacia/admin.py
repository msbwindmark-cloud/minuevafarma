from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from farmacia.models import Usuario, Rol, Auditoria, Empleado, Fichaje


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'puede_gestionar_usuarios', 'puede_gestionar_productos', 'puede_ventas', 'puede_auditoria']
    search_fields = ['nombre']


class UsuarioAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'nombre_completo', 'rol', 'is_active', 'two_factor_enabled', 'esta_bloqueado']
    list_filter = ['is_active', 'is_staff', 'rol', 'two_factor_enabled']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'numero_documento']
    ordering = ['username']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Datos personales', {'fields': ('first_name', 'last_name', 'email', 'tipo_documento', 'numero_documento', 'telefono', 'foto')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'rol', 'two_factor_enabled', 'debe_cambiar_password', 'groups', 'user_permissions')}),
        ('Seguridad', {'fields': ('intentos_fallidos', 'bloqueado_hasta', 'last_login_ip')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'email', 'password1', 'password2', 'rol')}),
    )


admin.site.register(Usuario, UsuarioAdmin)


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'usuario', 'accion', 'modelo', 'ip']
    list_filter = ['accion', 'modelo']
    search_fields = ['descripcion', 'ip']
    readonly_fields = [f.name for f in Auditoria._meta.fields]
    date_hierarchy = 'fecha'


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellidos', 'dni', 'puesto', 'activo', 'fecha_alta']
    list_filter = ['puesto', 'activo']
    search_fields = ['nombre', 'apellidos', 'dni']


@admin.register(Fichaje)
class FichajeAdmin(admin.ModelAdmin):
    list_display = ['empleado', 'entrada', 'salida', 'ip']
    list_filter = ['entrada']
    search_fields = ['empleado__nombre', 'empleado__apellidos']
    date_hierarchy = 'entrada'
