p = 'farmacia/views/ventas.py'
s = open(p, encoding='utf-8').read()

# 1. corregir constantes corruptas
s = s.replace('SITE_URL', 'SITE_URL').replace('PNG', 'PNG')
s = s.replace('DEFAULT_FROM_EMAIL', 'DEFAULT_FROM_EMAIL').replace('fail_silently=True', 'fail_silently=True')

# 2. insertar vista PDF despues de generar_qr (linea que termina en b64encode...)
pdf_fn = '''

@login_required
def venta_ticket_pdf(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    detalles = venta.detalles.all()
    link = request.build_absolute_uri('/ticket/verificar/' + str(venta.id) + '/')
    import qrcode as _qr
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet
    from io import BytesIO as _B
    buf = _B()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    ss = getSampleStyleSheet()
    elems = []
    elems.append(Paragraph('MiNuevaFarma', ss['Title']))
    elems.append(Paragraph('Ticket ' + venta.codigo + '  -  ' + venta.fecha.strftime('%d/%m/%Y %H:%M'), ss['Normal']))
    elems.append(Spacer(1, 6))
    data = [['Producto', 'Cant.', 'P.U.', 'Subtotal']]
    for d in detalles:
        data.append([d.nombre, str(d.cantidad), str(d.precio_unitario) + ' EUR', str(d.subtotal) + ' EUR'])
    data.append(['', '', 'TOTAL', str(venta.total) + ' EUR'])
    t = Table(data, colWidths=[80*mm, 20*mm, 30*mm, 30*mm])
    t.setStyle(_tbl_style())
    elems.append(t)
    elems.append(Spacer(1, 8))
    elems.append(Paragraph('Metodo: ' + venta.get_metodo_pago_display(), ss['Normal']))
    elems.append(Paragraph('Atendido por: ' + (str(venta.empleado) if venta.empleado else '-'), ss['Normal']))
    qr_img = _qr.make(link)
    qb = _B(); qr_img.save(qb, format='PNG'); qb.seek(0)
    elems.append(Spacer(1, 8))
    elems.append(RLImage(qb, width=40*mm, height=40*mm))
    elems.append(Paragraph('Escanea para verificar', ss['Normal']))
    doc.build(elems)
    resp = HttpResponse(buf.getvalue(), content_type='application/pdf')
    resp['Content-Disposition'] = 'attachment; filename="ticket_' + venta.codigo + '.pdf"'
    return resp


def _tbl_style():
    from reportlab.platypus import TableStyle
    return TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#f8f9fa')),
    ])
'''

if 'def venta_ticket_pdf' not in s:
    # insertar antes de '@login_required\ndef venta_enviar'
    marker = '@login_required\ndef venta_enviar'
    if marker in s:
        s = s.replace(marker, pdf_fn.strip() + '\n\n' + marker)
    else:
        s = s.rstrip() + pdf_fn

open(p, 'w', encoding='utf-8').write(s)
ok = all(k in s for k in ['def venta_ticket_pdf', 'SITE_URL', 'PNG', 'DEFAULT_FROM_EMAIL', 'fail_silently'])
print('PDF insertada y constantes OK:', ok)
