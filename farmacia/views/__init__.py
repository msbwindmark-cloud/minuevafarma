from .auth import (registro, login_view, logout_view, verificar_2fa,
                     password_reset_request, password_reset_confirm, perfil, toggle_2fa)
from .core import dashboard, auditoria_list
from .inventario import (producto_list, producto_create, producto_update,
                         producto_delete, producto_movimiento, movimiento_list,
                         categoria_list, categoria_create, categoria_update, categoria_delete,
                         proveedor_list, proveedor_create, proveedor_update, proveedor_delete)

__all__ = ['registro', 'login_view', 'logout_view', 'verificar_2fa',
           'password_reset_request', 'password_reset_confirm', 'perfil', 'toggle_2fa',
           'dashboard', 'auditoria_list',
           'producto_list', 'producto_create', 'producto_update', 'producto_delete',
           'producto_movimiento', 'movimiento_list',
           'categoria_list', 'categoria_create', 'categoria_update', 'categoria_delete',
           'proveedor_list', 'proveedor_create', 'proveedor_update', 'proveedor_delete']
