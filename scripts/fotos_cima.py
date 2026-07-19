import os, django, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from farmacia.models import Producto
from farmacia.cima import ficha_resumida

actualizados = 0
for p in Producto.objects.all():
    try:
        f = ficha_resumida(p.nombre)
    except Exception:
        f = None
    if f and f.get('foto'):
        p.foto_url = f['foto']
        p.save(update_fields=['foto_url'])
        actualizados += 1
        print('foto ->', p.nombre[:40])
print('Total con foto_url:', actualizados)
