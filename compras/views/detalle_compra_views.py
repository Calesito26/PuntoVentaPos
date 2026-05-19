from django.db.models import Q
from django.shortcuts import render

from compras.models import DetalleCompra
from compras.models import Proveedor
from inventario.models import Sede
from usuarios.decorators import administrador_required
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from openpyxl import Workbook
from django.contrib.auth.decorators import login_required
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

@administrador_required
def detalle_compra_list(request):
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    sede_id = request.GET.get('sede', '')
    proveedor_id = request.GET.get('proveedor', '')
    usuario_id = request.GET.get('usuario', '')
    buscar = request.GET.get('buscar', '').strip()

    sedes = Sede.objects.filter(activo=True).order_by('nombre')
    proveedores = Proveedor.objects.filter(activo=True).order_by('razon_social')
    User = get_user_model()
    usuarios = User.objects.filter(is_active=True).order_by('username')

    detalles = DetalleCompra.objects.select_related(
    'compra',
    'producto',
    'compra__sede',
    'compra__proveedor',
    'compra__responsable'
    ).all().order_by('-id')
    print(detalles.count())

    if fecha_inicio:
        detalles = detalles.filter(compra__fecha_compra__date__gte=fecha_inicio)

    if fecha_fin:
        detalles = detalles.filter(compra__fecha_compra__date__lte=fecha_fin)

    if sede_id:
        detalles = detalles.filter(compra__sede_id=sede_id)

    if proveedor_id:
        detalles = detalles.filter(compra__proveedor_id=proveedor_id)

    if usuario_id:
        detalles = detalles.filter(compra__responsable_id=usuario_id)

    if buscar:
        detalles = detalles.filter(
            Q(compra__codigo__icontains=buscar) |
            Q(producto__codigo__icontains=buscar) |
            Q(producto__nombre__icontains=buscar) |
            Q(compra__proveedor__razon_social__icontains=buscar)
        )

    total_compras = sum(detalle.subtotal for detalle in detalles)

    return render(
        request,
        'compras/detalle_compra_list.html',
        {
            'detalles': detalles,
            'sedes': sedes,
            'proveedores': proveedores,
            'usuarios': usuarios,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'sede_id': sede_id,
            'proveedor_id': proveedor_id,
            'usuario_id': usuario_id,
            'buscar': buscar,
            'total_compras': total_compras,
        }
    )

@login_required
def detalle_compra_excel(request):

    detalles = DetalleCompra.objects.select_related(
        'compra',
        'producto',
        'compra__proveedor',
        'compra__sede'
    )

    wb = Workbook()
    ws = wb.active
    ws.title = 'Detalle Compras'

    encabezados = [
        'Factura',
        'Bodega',
        'Fecha',
        'Proveedor',
        'Producto',
        'Precio Compra',
        'Devuelto',
        'Cantidad',
        'Total'
    ]

    ws.append(encabezados)

    for detalle in detalles:
        ws.append([
            detalle.compra.codigo,
            detalle.compra.sede.nombre,
            detalle.compra.fecha_compra.strftime('%Y-%m-%d %H:%M'),
            detalle.compra.proveedor.razon_social,
            detalle.producto.nombre,
            float(detalle.precio_compra),
            float(detalle.cantidad_devuelta),
            float(detalle.cantidad),
            float(detalle.subtotal)
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename=detalle_compras.xlsx'

    wb.save(response)

    return response


@administrador_required
@login_required
def detalle_compra_pdf(request):
    detalles = DetalleCompra.objects.select_related(
        'compra',
        'producto',
        'compra__proveedor',
        'compra__sede'
    ).all().order_by('-id')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=detalle_compras.pdf'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y = height - 50

    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(40, y, 'Detalle de compras')
    y -= 35

    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawString(40, y, 'Item')
    pdf.drawString(75, y, 'Factura')
    pdf.drawString(145, y, 'Producto')
    pdf.drawString(330, y, 'Proveedor')
    pdf.drawString(430, y, 'Cant.')
    pdf.drawString(475, y, 'Devuelto')
    pdf.drawString(535, y, 'Total')
    y -= 18

    pdf.setFont('Helvetica', 8)

    total_general = 0

    for index, detalle in enumerate(detalles, start=1):
        if y < 50:
            pdf.showPage()
            y = height - 50
            pdf.setFont('Helvetica', 8)

        total_general += detalle.subtotal

        pdf.drawString(40, y, str(index))
        pdf.drawString(75, y, str(detalle.compra.codigo)[:12])
        pdf.drawString(145, y, str(detalle.producto.nombre)[:28])
        pdf.drawString(330, y, str(detalle.compra.proveedor.razon_social)[:18])
        pdf.drawString(430, y, str(int(detalle.cantidad)))
        pdf.drawString(475, y, str(int(detalle.cantidad_devuelta)))
        pdf.drawString(535, y, f'S/ {detalle.subtotal:.2f}')

        y -= 18

    y -= 20
    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawString(430, y, f'TOTAL: S/ {total_general:.2f}')

    pdf.save()
    return response