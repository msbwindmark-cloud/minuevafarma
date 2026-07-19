from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from farmacia.models import (
    Usuario, Rol, Auditoria, Empleado, Fichaje,
    Categoria, Proveedor, Producto, MovimientoStock,
    Venta, DetalleVenta, Cliente, Recordatorio, Caja,
    PedidoProveedor, LineaPedido,
)


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


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'cif', 'email', 'telefono', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'cif', 'email']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'cn', 'categoria', 'proveedor', 'stock_actual', 'stock_minimo', 'precio_venta', 'caducidad', 'activo']
    list_filter = ['activo', 'categoria', 'proveedor', 'unidad']
    search_fields = ['nombre', 'codigo', 'cn']
    readonly_fields = ['creado', 'actualizado']


@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'producto', 'tipo', 'cantidad', 'stock_resultante', 'motivo', 'usuario']
    list_filter = ['tipo']
    search_fields = ['producto__nombre', 'motivo']
    date_hierarchy = 'fecha'
    readonly_fields = [f.name for f in MovimientoStock._meta.fields]


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ['codigo', 'nombre', 'cantidad', 'precio_unitario', 'subtotal']


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'fecha', 'empleado', 'cliente_nombre', 'metodo_pago', 'total', 'anulada']
    list_filter = ['metodo_pago', 'anulada']
    search_fields = ['codigo', 'cliente_nombre', 'cliente_email']
    date_hierarchy = 'fecha'
    inlines = [DetalleVentaInline]


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ['venta', 'producto', 'nombre', 'cantidad', 'precio_unitario', 'subtotal']
    search_fields = ['nombre', 'codigo']


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono', 'email', 'puntos', 'fecha_alta']
    search_fields = ['nombre', 'telefono', 'email']
    list_filter = ['puntos']
    readonly_fields = ['fecha_alta']


@admin.register(Recordatorio)
class RecordatorioAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'cliente_nombre', 'cliente_email', 'producto', 'enviado', 'fecha_envio', 'creado']
    list_filter = ['tipo', 'enviado']
    search_fields = ['cliente_nombre', 'cliente_email', 'producto', 'mensaje']
    readonly_fields = ['creado']


@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'fecha', 'fondo_inicial', 'efectivo', 'tarjeta', 'total', 'usuario']
    list_filter = ['tipo']
    search_fields = ['notas']
    date_hierarchy = 'fecha'
    readonly_fields = ['fecha']


@admin.register(PedidoProveedor)
class PedidoProveedorAdmin(admin.ModelAdmin):
    list_display = ['id', 'proveedor', 'fecha', 'estado', 'creado_por']
    list_filter = ['estado', 'proveedor']
    search_fields = ['notas']
    date_hierarchy = 'fecha'


@admin.register(LineaPedido)
class LineaPedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'producto', 'cantidad_sugerida', 'cantidad_pedida']
    search_fields = ['producto__nombre']
