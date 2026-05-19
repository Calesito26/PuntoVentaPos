from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

import openpyxl

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from compras.models import DevolucionCompra
from usuarios.decorators import administrador_required


def filtrar_devoluciones_compra(request):
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    usuario_id = request.GET.get('usuario', '')
    buscar = request.GET.get('buscar', '').strip()

    devoluciones = DevolucionCompra.objects.select_related(
        'compra',
        'responsable',
        'proveedor'
    ).all()

    if fecha_inicio:
        devoluciones = devoluciones.filter(fecha__date__gte=fecha_inicio)

    if fecha_fin:
        devoluciones = devoluciones.filter(fecha__date__lte=fecha_fin)

    if usuario_id:
        devoluciones = devoluciones.filter(responsable_id=usuario_id)

    if buscar:
        devoluciones = devoluciones.filter(
            Q(codigo__icontains=buscar) |
            Q(compra__codigo__icontains=buscar) |
            Q(proveedor__razon_social__icontains=buscar)
        )

    return devoluciones.order_by('-fecha')


@administrador_required
def devolucion_compra_list(request):
    User = get_user_model()

    devoluciones = filtrar_devoluciones_compra(request)
    usuarios = User.objects.filter(is_active=True).order_by('username')

    total_devoluciones = sum(dev.valor for dev in devoluciones)

    return render(
        request,
        'compras/devolucion_compra_list.html',
        {
            'devoluciones': devoluciones,
            'usuarios': usuarios,
            'fecha_inicio': request.GET.get('fecha_inicio', ''),
            'fecha_fin': request.GET.get('fecha_fin', ''),
            'usuario_id': request.GET.get('usuario', ''),
            'buscar': request.GET.get('buscar', ''),
            'total_devoluciones': total_devoluciones,
        }
    )


@administrador_required
def devolucion_compra_excel(request):
    devoluciones = filtrar_devoluciones_compra(request)

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Devoluciones compras'

    hoja.append([
        'Item',
        'Devolución',
        'Factura',
        'Fecha y hora',
        'Responsable',
        'Proveedor',
        'Valor',
        'Estado',
    ])

    total = 0

    for index, dev in enumerate(devoluciones, start=1):
        total += dev.valor

        hoja.append([
            index,
            dev.codigo,
            dev.compra.codigo,
            dev.fecha.strftime('%Y-%m-%d %H:%M:%S'),
            dev.responsable.username if dev.responsable else '',
            dev.proveedor.razon_social if dev.proveedor else '',
            float(dev.valor),
            dev.estado,
        ])

    hoja.append([])
    hoja.append(['', '', '', '', '', 'TOTAL', float(total), ''])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=devoluciones_compras.xlsx'

    workbook.save(response)
    return response


@administrador_required
def devolucion_compra_pdf(request):
    devoluciones = filtrar_devoluciones_compra(request)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=devoluciones_compras.pdf'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y = height - 50

    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(40, y, 'Devoluciones Compras')
    y -= 35

    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawString(40, y, 'Item')
    pdf.drawString(75, y, 'Devolucion')
    pdf.drawString(155, y, 'Factura')
    pdf.drawString(235, y, 'Fecha')
    pdf.drawString(350, y, 'Proveedor')
    pdf.drawString(470, y, 'Valor')
    pdf.drawString(530, y, 'Estado')
    y -= 18

    pdf.setFont('Helvetica', 8)

    total = 0

    for index, dev in enumerate(devoluciones, start=1):
        if y < 50:
            pdf.showPage()
            y = height - 50
            pdf.setFont('Helvetica', 8)

        total += dev.valor

        pdf.drawString(40, y, str(index))
        pdf.drawString(75, y, dev.codigo)
        pdf.drawString(155, y, dev.compra.codigo)
        pdf.drawString(235, y, dev.fecha.strftime('%Y-%m-%d %H:%M'))
        pdf.drawString(350, y, str(dev.proveedor.razon_social)[:18])
        pdf.drawString(470, y, f'S/ {dev.valor:.2f}')
        pdf.drawString(530, y, dev.estado)

        y -= 18

    y -= 20
    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawString(430, y, f'TOTAL: S/ {total:.2f}')

    pdf.save()
    return response