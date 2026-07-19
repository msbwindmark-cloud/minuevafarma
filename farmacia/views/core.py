from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import F
from farmacia.models import Auditoria, Usuario, Producto


@login_required
def dashboard(request):
    total_usuarios = Usuario.objects.count()
    ultimos_logs = Auditoria.objects.select_related('usuario').all()[:10]
    hoy = timezone.now().date()
    productos_bajo = Producto.objects.filter(stock_actual__lte=F('stock_minimo')).count()
    stats = {
        'usuarios': total_usuarios,
        'logins_hoy': Auditoria.objects.filter(accion='LOGIN', fecha__date=hoy).count(),
        'bloqueados': Usuario.objects.filter(bloqueado_hasta__gt=timezone.now()).count(),
        'stock_bajo': productos_bajo,
    }
    return render(request, 'farmacia/dashboard.html',
                  {'stats': stats, 'ultimos_logs': ultimos_logs})


@login_required
def auditoria_list(request):
    logs = Auditoria.objects.select_related('usuario').all()
    return render(request, 'farmacia/auditoria.html', {'logs': logs})
