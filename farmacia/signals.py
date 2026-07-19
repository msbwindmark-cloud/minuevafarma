from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from farmacia.models import Producto, MovimientoStock, Auditoria, Categoria, Proveedor, Empleado, Fichaje


@receiver(pre_save, sender=Producto)
def _producto_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Producto.objects.get(pk=instance.pk)
            instance._stock_previo = old.stock_actual
        except Producto.DoesNotExist:
            instance._stock_previo = None


@receiver(post_save, sender=Producto)
def _producto_post_save(sender, instance, created, **kwargs):
    if created:
        Auditoria.objects.create(
            accion='CREATE', modelo='Producto',
            objeto_id=str(instance.id),
            descripcion=f"Alta de producto: {instance.nombre} ({instance.codigo})")
    else:
        Auditoria.objects.create(
            accion='UPDATE', modelo='Producto',
            objeto_id=str(instance.id),
            descripcion=f"Modificación de producto: {instance.nombre}")
        prev = getattr(instance, '_stock_previo', None)
        if prev is not None and prev != instance.stock_actual:
            diff = instance.stock_actual - prev
            MovimientoStock.objects.create(
                producto=instance,
                tipo='AJUSTE',
                cantidad=diff,
                stock_resultante=instance.stock_actual,
                motivo='Ajuste manual de stock',
            )


@receiver(post_save, sender=Categoria)
def _categoria_post_save(sender, instance, created, **kwargs):
    Auditoria.objects.create(
        accion='CREATE' if created else 'UPDATE', modelo='Categoria',
        objeto_id=str(instance.id), descripcion=f"Categoría: {instance.nombre}")


@receiver(post_save, sender=Proveedor)
def _proveedor_post_save(sender, instance, created, **kwargs):
    Auditoria.objects.create(
        accion='CREATE' if created else 'UPDATE', modelo='Proveedor',
        objeto_id=str(instance.id), descripcion=f"Proveedor: {instance.nombre}")


@receiver(post_save, sender=Empleado)
def _empleado_post_save(sender, instance, created, **kwargs):
    Auditoria.objects.create(
        accion='CREATE' if created else 'UPDATE', modelo='Empleado',
        objeto_id=str(instance.id), descripcion=f"Empleado: {instance.nombre} {instance.apellidos}")


@receiver(post_save, sender=Fichaje)
def _fichaje_post_save(sender, instance, created, **kwargs):
    accion = 'CREATE' if created else 'UPDATE'
    descripcion = f"Fichaje {'entrada' if created else 'actualizacion'} de {instance.empleado}"
    if instance.salida and not created:
        descripcion = f"Fichaje salida de {instance.empleado}"
    Auditoria.objects.create(accion=accion, modelo='Fichaje',
        objeto_id=str(instance.id), descripcion=descripcion)
