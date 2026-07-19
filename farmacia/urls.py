from django.urls import path
from farmacia import views

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
    path('movimientos/', views.movimiento_list, name='movimiento_list'),

    path('categorias/', views.categoria_list, name='categoria_list'),
    path('categorias/nueva/', views.categoria_create, name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.categoria_update, name='categoria_update'),
    path('categorias/<int:pk>/eliminar/', views.categoria_delete, name='categoria_delete'),
    path('proveedores/', views.proveedor_list, name='proveedor_list'),
    path('proveedores/nuevo/', views.proveedor_create, name='proveedor_create'),
    path('proveedores/<int:pk>/editar/', views.proveedor_update, name='proveedor_update'),
    path('proveedores/<int:pk>/eliminar/', views.proveedor_delete, name='proveedor_delete'),
]
