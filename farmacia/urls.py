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
]
