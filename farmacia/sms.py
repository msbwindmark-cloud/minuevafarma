import os
from django.conf import settings


def enviar_sms(telefono, mensaje):
    """Envio SMS. Si hay credenciales de Twilio configuradas, envia real.
    Si no, simula (lo registra en consola)."""
    sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
    from_ = getattr(settings, 'TWILIO_FROM_NUMBER', None)
    if sid and token and from_:
        try:
            from twilio.rest import Client
            client = Client(sid, token)
            client.messages.create(body=mensaje, from_=from_, to=telefono)
            return True
        except Exception as e:
            print('Twilio error:', e)
            return False
    # Modo simulado
    print('SMS simulado ->', telefono, ':', mensaje)
    return True

