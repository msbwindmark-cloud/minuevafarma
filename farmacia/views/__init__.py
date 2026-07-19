from .auth import (registro, login_view, logout_view, verificar_2fa,
                     password_reset_request, password_reset_confirm, perfil, toggle_2fa)
from .core import dashboard, auditoria_list
from .inventario import (producto_list, producto_create, producto_update,
                         producto_delete, producto_movimiento, movimiento_list,
                         categoria_list, categoria_create, categoria_update, categoria_delete,
                         proveedor_list, proveedor_create, proveedor_update, proveedor_delete)
from .empleados import (empleado_list, empleado_create, empleado_update,
                        empleado_delete, fichar, fichaje_list)

__all__ = ['registro', 'login_view', 'logout_view', 'verificar_2fa',
           'password_reset_request', 'password_reset_confirm', 'perfil', 'toggle_2fa',
           'dashboard', 'auditoria_list',
           'producto_list', 'producto_create', 'producto_update', 'producto_delete',
           'producto_movimiento', 'movimiento_list',
           'categoria_list', 'categoria_create', 'categoria_update', 'categoria_delete',
           'proveedor_list', 'proveedor_create', 'proveedor_update', 'proveedor_delete',
           'empleado_list', 'empleado_create', 'empleado_update', 'empleado_delete',
            'fichar', 'fichaje_list',
            'venta_nueva', 'venta_agregar', 'venta_quitar', 'venta_list', 'venta_ticket', 'venta_verificar', 'venta_enviar', 'venta_ticket_pdf',
]
from .ventas import (venta_nueva, venta_agregar, venta_quitar, venta_list, venta_ticket, venta_verificar, venta_enviar, venta_ticket_pdf)
from .api import venta_offline
from .api_offline import api_login, api_productos, offline_app
from .pwa_views import service_worker, manifest_json


