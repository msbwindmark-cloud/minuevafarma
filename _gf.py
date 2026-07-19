p = 'farmacia/views/ventas.py'
s = open(p, encoding='utf-8').read()
s = s.replace('DEFAULT_FROM_EMAIL', 'DEFAULT_FROM_EMAIL')
s = s.replace('fail_silently=True', 'fail_silently=True')
open(p, 'w', encoding='utf-8').write(s)
print('DEFAULT_FROM_EMAIL' in s, 'fail_silently=True' in s)
