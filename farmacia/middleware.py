import json
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from django.utils import timezone
from farmacia.models import Auditoria


class AuditMiddleware(MiddlewareMixin):
    RUTAS_AUDITABLES = {
        'login': 'LOGIN',
        'logout': 'LOGOUT',
        'registro': 'REGISTRO',
        'verificar_2fa': '2FA',
    }

    def process_request(self, request):
        request._audit_start = timezone.now()
        return None

    def process_response(self, request, response):
        try:
            resolver = resolve(request.path_info)
            nombre = resolver.url_name
            if nombre in self.RUTAS_AUDITABLES and request.method == 'POST':
                accion = self.RUTAS_AUDITABLES[nombre]
                user = getattr(request, 'user', None)
                usuario = user if (user and user.is_authenticated) else None
                Auditoria.objects.create(
                    usuario=usuario,
                    accion=accion,
                    modelo='Auth',
                    descripcion=f"{accion} desde {request.path_info}",
                    ip=self._get_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                )
        except Exception:
            pass
        return response

    def _get_ip(self, request):
        xf = request.META.get('HTTP_X_FORWARDED_FOR')
        if xf:
            return xf.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
