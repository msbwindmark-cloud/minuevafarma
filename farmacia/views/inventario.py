from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from farmacia.models import Producto, Categoria, Proveedor, MovimientoStock, Auditoria
from farmacia.forms import ProductoForm, CategoriaForm, ProveedorForm, MovimientoForm


def _ip(request):
    xf = request.META.get('HTTP_X_FORWARDED_FOR')
    return xf.split(',')[0].strip() if xf else request.META.get('REMOTE_ADDR')


@login_required
def producto_list(request):
    q = request.GET.get('q', '')
    qs = Producto.objects.select_related('categoria', 'proveedor')
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q) | Q(ubicacion__icontains=q))
    productos = qs.all()
    return render(request, 'farmacia/producto_list.html',
                  {'productos': productos, 'q': q})


@login_required
def producto_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado.')
            return redirect('producto_list')
    else:
        form = ProductoForm()
    return render(request, 'farmacia/producto_form.html', {'form': form, 'titulo': 'Nuevo producto'})


@login_required
def producto_update(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado.')
            return redirect('producto_list')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'farmacia/producto_form.html', {'form': form, 'titulo': 'Editar producto'})


@login_required
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        Auditoria.objects.create(accion='DELETE', modelo='Producto',
            objeto_id=str(producto.id),
            descripcion=f"Eliminación de producto: {producto.nombre}",
            usuario=request.user, ip=_ip(request))
        producto.delete()
        messages.success(request, 'Producto eliminado.')
        return redirect('producto_list')
    return render(request, 'farmacia/producto_confirm_delete.html', {'producto': producto})


@login_required
def producto_movimiento(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            m = form.save(commit=False)
            m.producto = producto
            m.usuario = request.user
            m.ip = _ip(request)
            cant = m.cantidad
            if m.tipo == 'ENTRADA':
                producto.stock_actual += cant
            elif m.tipo == 'SALIDA':
                if cant > producto.stock_actual:
                    messages.error(request, f'Stock insuficiente. Solo hay {producto.stock_actual}.')
                    return render(request, 'farmacia/producto_movimiento.html', {'form': form, 'producto': producto})
                producto.stock_actual -= cant
            else:
                if cant < 0:
                    messages.error(request, 'El stock no puede ser negativo.')
                    return render(request, 'farmacia/producto_movimiento.html', {'form': form, 'producto': producto})
                producto.stock_actual = cant
            m.stock_resultante = producto.stock_actual
            producto.save()
            m.save()
            Auditoria.objects.create(accion='UPDATE', modelo='Producto',
                objeto_id=str(producto.id),
                descripcion=f"Movimiento {m.tipo} {cant} de {producto.nombre}",
                usuario=request.user, ip=_ip(request))
            messages.success(request, 'Movimiento registrado.')
            return redirect('producto_list')
    else:
        form = MovimientoForm()
    return render(request, 'farmacia/producto_movimiento.html', {'form': form, 'producto': producto})


@login_required
def movimiento_list(request):
    movs = MovimientoStock.objects.select_related('producto', 'usuario').all()[:100]
    return render(request, 'farmacia/movimiento_list.html', {'movs': movs})


@login_required
def categoria_list(request):
    cats = Categoria.objects.all()
    return render(request, 'farmacia/categoria_list.html', {'cats': cats})


@login_required
def categoria_create(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada.')
            return redirect('categoria_list')
    else:
        form = CategoriaForm()
    return render(request, 'farmacia/categoria_form.html', {'form': form, 'titulo': 'Nueva categoría'})


@login_required
def categoria_update(request, pk):
    cat = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada.')
            return redirect('categoria_list')
    else:
        form = CategoriaForm(instance=cat)
    return render(request, 'farmacia/categoria_form.html', {'form': form, 'titulo': 'Editar categoría'})


@login_required
def categoria_delete(request, pk):
    cat = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        Auditoria.objects.create(accion='DELETE', modelo='Categoria',
            objeto_id=str(cat.id), descripcion=f"Eliminación de categoría: {cat.nombre}",
            usuario=request.user, ip=_ip(request))
        cat.delete()
        messages.success(request, 'Categoría eliminada.')
        return redirect('categoria_list')
    return render(request, 'farmacia/categoria_confirm_delete.html',
                  {'obj': cat, 'tipo': 'categoría', 'back': 'categoria_list'})


@login_required
def proveedor_list(request):
    provs = Proveedor.objects.all()
    return render(request, 'farmacia/proveedor_list.html', {'provs': provs})


@login_required
def proveedor_create(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor creado.')
            return redirect('proveedor_list')
    else:
        form = ProveedorForm()
    return render(request, 'farmacia/proveedor_form.html', {'form': form, 'titulo': 'Nuevo proveedor'})


@login_required
def proveedor_update(request, pk):
    prov = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=prov)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor actualizado.')
            return redirect('proveedor_list')
    else:
        form = ProveedorForm(instance=prov)
    return render(request, 'farmacia/proveedor_form.html', {'form': form, 'titulo': 'Editar proveedor'})


@login_required
def proveedor_delete(request, pk):
    prov = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        Auditoria.objects.create(accion='DELETE', modelo='Proveedor',
            objeto_id=str(prov.id), descripcion=f"Eliminación de proveedor: {prov.nombre}",
            usuario=request.user, ip=_ip(request))
        prov.delete()
        messages.success(request, 'Proveedor eliminado.')
        return redirect('proveedor_list')
    return render(request, 'farmacia/categoria_confirm_delete.html',
                  {'obj': prov, 'tipo': 'proveedor', 'back': 'proveedor_list'})
