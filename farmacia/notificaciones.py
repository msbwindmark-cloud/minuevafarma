from farmacia.models import Recordatorio


def crear_recordatorios_venta(venta):
    nombre = (venta.cliente_nombre or "").strip()
    email = (venta.cliente_email or "").strip()
    telefono = (venta.cliente_telefono or "").strip()
    if not (email or telefono):
        return
    productos = list(venta.detalles.values_list("nombre", flat=True))
    for p in productos:
        Recordatorio.objects.create(
            cliente_nombre=nombre, cliente_email=email, cliente_telefono=telefono,
            tipo="TRATAMIENTO",
            producto=p,
            mensaje="Hola %s, recuerda seguir tu tratamiento con %s. Equipo MiNuevaFarma." % (nombre or "cliente", p)
        )


def enviar_recordatorio(r):
    enviado = False
    if r.cliente_telefono:
        try:
            from farmacia.sms import enviar_sms
            enviar_sms(r.cliente_telefono, r.mensaje)
            enviado = True
        except Exception:
            pass
    if not enviado and r.cliente_email:
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            send_mail("MiNuevaFarma - Recordatorio", r.mensaje, settings.DEFAULT_FROM_EMAIL, [r.cliente_email], fail_silently=True)
            enviado = True
        except Exception:
            pass
    return enviado
