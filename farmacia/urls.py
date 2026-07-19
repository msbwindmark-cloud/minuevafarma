from django.urls import path
from farmacia import views
from farmacia.views import api as api_views
from farmacia.views.api_offline import api_producto_detalle
from farmacia.views import caja_views as views_caja
from farmacia.views.ventas import venta_anular
from farmacia.views import export_views as exp
from farmacia.views.clientes_views import cliente_list as _cliente_list
from farmacia.views.recordatorios_views import recordatorio_list, recordatorio_crear, recordatorio_reenviar, campana_enviar
from farmacia.views.pedidos_views import pedido_sugerir, pedido_generar, pedido_list, pedido_detalle, pedido_pdf


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro, name='registro'),
    path('2fa/', views.verificar_2fa, name='verificar_2fa'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    path('perfil/', views.perfil, name='perfil'),
    path('toggle-2fa/', views.toggle_2fa, name='toggle_2fa'),
    path('auditoria/', views.auditoria_list, name='auditoria'),

    path('productos/', views.producto_list, name='producto_list'),
    path('productos/nuevo/', views.producto_create, name='producto_create'),
    path('productos/<uuid:pk>/editar/', views.producto_update, name='producto_update'),
    path('productos/<uuid:pk>/eliminar/', views.producto_delete, name='producto_delete'),
    path('productos/<uuid:pk>/movimiento/', views.producto_movimiento, name='producto_movimiento'),
    path('productos/<uuid:pk>/ficha/', views.producto_ficha, name='producto_ficha'),
    path('movimientos/', views.movimiento_list, name='movimiento_list'),

    path('categorias/', views.categoria_list, name='categoria_list'),
    path('categorias/nueva/', views.categoria_create, name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.categoria_update, name='categoria_update'),
    path('categorias/<int:pk>/eliminar/', views.categoria_delete, name='categoria_delete'),
    path('proveedores/', views.proveedor_list, name='proveedor_list'),
    path('proveedores/nuevo/', views.proveedor_create, name='proveedor_create'),
    path('proveedores/<int:pk>/editar/', views.proveedor_update, name='proveedor_update'),
    path('proveedores/<int:pk>/eliminar/', views.proveedor_delete, name='proveedor_delete'),

    path('empleados/', views.empleado_list, name='empleado_list'),
    path('empleados/nuevo/', views.empleado_create, name='empleado_create'),
    path('empleados/<uuid:pk>/editar/', views.empleado_update, name='empleado_update'),
    path('empleados/<uuid:pk>/eliminar/', views.empleado_delete, name='empleado_delete'),
    path('fichar/', views.fichar, name='fichar'),
    path('fichajes/', views.fichaje_list, name='fichaje_list'),

    path('ventas/', views.venta_list, name='venta_list'),
    path('ventas/nueva/', views.venta_nueva, name='venta_nueva'),
    path('ventas/agregar/', views.venta_agregar, name='venta_agregar'),
    path('ventas/quitar/<uuid:pid>/', views.venta_quitar, name='venta_quitar'),
    path('ventas/ticket/<uuid:pk>/', views.venta_ticket, name='venta_ticket'),
    path('ventas/ticket/pdf/<uuid:pk>/', views.venta_ticket_pdf, name='venta_ticket_pdf'),
    path('ventas/enviar/<uuid:pk>/', views.venta_enviar, name='venta_enviar'),
    path('ventas/anular/<uuid:pk>/', venta_anular, name='venta_anular'),
    path('caja/', views_caja.caja_view, name='caja'),
    path('caja/abrir/', views_caja.caja_abrir, name='caja_abrir'),
    path('export/productos/<str:fmt>/', exp.export_productos, name='export_productos'),
    path('export/ventas/<str:fmt>/', exp.export_ventas, name='export_ventas'),
    path('export/clientes/<str:fmt>/', exp.export_clientes, name='export_clientes'),
    path('export/movimientos/<str:fmt>/', exp.export_movimientos, name='export_movimientos'),
    path('export/caja/<str:fmt>/', exp.export_caja, name='export_caja'),
    path('clientes/', _cliente_list, name='cliente_list'),
    path('recordatorios/', recordatorio_list, name='recordatorio_list'),
    path('recordatorios/crear/', recordatorio_crear, name='recordatorio_crear'),
    path('recordatorios/reenviar/<uuid:pk>/', recordatorio_reenviar, name='recordatorio_reenviar'),
    path('campanas/', campana_enviar, name='campana_enviar'),
    path('pedidos/sugerir/', pedido_sugerir, name='pedido_sugerir'),
    path('pedidos/generar/', pedido_generar, name='pedido_generar'),
    path('pedidos/', pedido_list, name='pedido_list'),
    path('pedidos/<uuid:pk>/', pedido_detalle, name='pedido_detalle'),
    path('pedidos/<uuid:pk>/pdf/', pedido_pdf, name='pedido_pdf'),
    path('export/categorias/<str:fmt>/', exp.export_categorias, name='export_categorias'),
    path('export/proveedores/<str:fmt>/', exp.export_proveedores, name='export_proveedores'),
    path('export/alertas/<str:fmt>/', exp.export_alertas, name='export_alertas'),
    path('ticket/verificar/<uuid:pk>/', views.venta_verificar, name='venta_verificar'),
    path('api/venta/offline/', views.venta_offline, name='venta_offline'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/productos/', views.api_productos, name='api_productos'),
    path('api/producto/<uuid:pk>/', api_producto_detalle, name='api_producto_detalle'),
    path('api/interacciones/', api_views.chequear_interacciones, name='chequear_interacciones'),
    path('api/interacciones/carrito/', api_views.chequear_interacciones_carrito, name='chequear_interacciones_carrito'),
    path('api/sugerencias/', api_views.sugerencias_api, name='sugerencias_api'),
    path('api/historia/', api_views.historia_cliente, name='historia_cliente'),
    path('offline/', views.offline_app, name='offline_app'),
]
