from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse

from farmacia.models import Empleado, Fichaje, Auditoria
from farmacia.forms import EmpleadoForm


def _ip(request):
    xf = request.META.get('HTTP_X_FORWARDED_FOR')
    return xf.split(',')[0].strip() if xf else request.META.get('REMOTE_ADDR')


@login_required
def empleado_list(request):
    emps = Empleado.objects.all()
    hoy = timezone.now().date()
    fichajes_hoy = Fichaje.objects.filter(entrada__date=hoy).count()
    return render(request, 'farmacia/empleado_list.html', {'emps': emps, 'fichajes_hoy': fichajes_hoy})


@login_required
def empleado_create(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empleado dado de alta.')
            return redirect('empleado_list')
    else:
        form = EmpleadoForm()
    return render(request, 'farmacia/empleado_form.html', {'form': form, 'titulo': 'Nuevo empleado'})


@login_required
def empleado_update(request, pk):
    emp = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES, instance=emp)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empleado actualizado.')
            return redirect('empleado_list')
    else:
        form = EmpleadoForm(instance=emp)
    return render(request, 'farmacia/empleado_form.html', {'form': form, 'titulo': 'Editar empleado'})


@login_required
def empleado_delete(request, pk):
    emp = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        Auditoria.objects.create(accion='DELETE', modelo='Empleado',
            objeto_id=str(emp.id), descripcion='Eliminacion de empleado: ' + str(emp),
            usuario=request.user, ip=_ip(request))
        emp.delete()
        messages.success(request, 'Empleado eliminado.')
        return redirect('empleado_list')
    return render(request, 'farmacia/categoria_confirm_delete.html',
                  {'obj': emp, 'tipo': 'empleado', 'back': 'empleado_list'})


@login_required
def fichar(request):
    emp_id = request.POST.get('empleado') or request.GET.get('empleado')
    if not emp_id:
        return JsonResponse({'ok': False, 'msg': 'Sin empleado'})
    emp = get_object_or_404(Empleado, pk=emp_id)
    abierto = emp.fichado_hoy()
    if abierto:
        abierto.salida = timezone.now()
        abierto.ip = _ip(request)
        abierto.save()
        msg = 'Salida registrada para ' + emp.nombre
    else:
        Fichaje.objects.create(empleado=emp, entrada=timezone.now(), ip=_ip(request))
        msg = 'Entrada registrada para ' + emp.nombre
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'msg': msg})
    messages.success(request, msg)
    return redirect('empleado_list')


@login_required
def fichaje_list(request):
    fichajes = Fichaje.objects.select_related('empleado').all()[:200]
    return render(request, 'farmacia/fichaje_list.html', {'fichajes': fichajes})

