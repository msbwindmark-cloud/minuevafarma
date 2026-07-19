from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from farmacia.models import Cliente


@login_required
def cliente_list(request):
    q = request.GET.get('q', '')
    qs = Cliente.objects.all()
    if q:
        qs = qs.filter(nombre__icontains=q) | qs.filter(email__icontains=q) | qs.filter(telefono__icontains=q)
    clientes = qs.order_by('nombre')
    return render(request, 'farmacia/cliente_list.html', {'clientes': clientes, 'q': q})
