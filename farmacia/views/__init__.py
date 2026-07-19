from .auth import (registro, login_view, logout_view, verificar_2fa,
                     password_reset_request, password_reset_confirm, perfil, toggle_2fa)
from .core import dashboard, auditoria_list

__all__ = ['registro', 'login_view', 'logout_view', 'verificar_2fa',
           'password_reset_request', 'password_reset_confirm', 'perfil', 'toggle_2fa',
           'dashboard', 'auditoria_list']
