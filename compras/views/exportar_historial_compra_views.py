import openpyxl

from django.db.models import Q
from django.http import HttpResponse

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from compras.models import Compra
from usuarios.decorators import administrador_required


def obtener_compras_filtradas(request):
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    estado = request.GET.get('estado', '')
    sede_id = request.GET.get('sede', '')
    buscar = request.GET.get('buscar', '').strip()

    compras = Compra.objects.select_related(
        'proveedor',
        'sede',
        'responsable'
    ).all()

    if fecha_inicio:
        compras = compras.filter(fecha_compra__date__gte=fecha_inicio)

    if fecha_fin:
        compras = compras.filter(fecha_compra__date__lte=fecha_fin)

    if estado:
        compras = compras.filter(estado=estado)

    if sede_id:
        compras = compras.filter(sede_id=sede_id)

    if buscar:
        compras = compras.filter(
            Q(codigo__icontains=buscar) |
            Q(numero_comprobante__icontains=buscar) |
            Q(proveedor__razon_social__icontains=buscar) |
            Q(proveedor__numero_documento__icontains=buscar)
        )

    return compras.order_by('-fecha_compra')


@administrador_required
def exportar_historial_compras_excel(request):
    compras = obtener_compras_filtradas(request)

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Historial compras'

    hoja.append([
        'Item',
        'Factura',
        'Bodega',
        'Factura proveedor',
        'Fecha y hora',
        'Proveedor',
        'Atendió',
        'Método de pago',
        'Valor compra',
        'Salió de caja',
        'Estado',
    ])

    total = 0

    for index, compra in enumerate(compras, start=1):
        total += compra.total

        hoja.append([
            index,
            compra.codigo,
            compra.sede.nombre,
            compra.numero_comprobante or '',
            compra.fecha_compra.strftime('%d/%m/%Y %H:%M'),
            compra.proveedor.razon_social,
            compra.responsable.username if compra.responsable else '',
            'EFECTIVO',
            float(compra.total),
            'SI',
            compra.estado,
        ])

    hoja.append([])
    hoja.append(['', '', '', '', '', '', '', 'TOTAL', float(total)])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=historial_compras.xlsx'

    workbook.save(response)
    return response


@administrador_required
def exportar_historial_compras_pdf(request):
    compras = obtener_compras_filtradas(request)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=historial_compras.pdf'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y = height - 40

    pdf.setFont('Helvetica-Bold', 14)
    pdf.drawString(40, y, 'Historial de compras')
    y -= 28

    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawString(40, y, 'Item')
    pdf.drawString(70, y, 'Factura')
    pdf.drawString(140, y, 'Bodega')
    pdf.drawString(230, y, 'Proveedor')
    pdf.drawString(390, y, 'Total')
    pdf.drawString(470, y, 'Estado')
    y -= 15

    pdf.setFont('Helvetica', 8)

    total = 0

    for index, compra in enumerate(compras, start=1):
        total += compra.total

        if y < 50:
            pdf.showPage()
            y = height - 40
            pdf.setFont('Helvetica', 8)

        pdf.drawString(40, y, str(index))
        pdf.drawString(70, y, compra.codigo[:12])
        pdf.drawString(140, y, compra.sede.nombre[:14])
        pdf.drawString(230, y, compra.proveedor.razon_social[:24])
        pdf.drawString(390, y, f'S/ {compra.total:.2f}')
        pdf.drawString(470, y, compra.estado)

        y -= 15

    y -= 15
    pdf.setFont('Helvetica-Bold', 9)
    pdf.drawString(390, y, f'TOTAL: S/ {total:.2f}')

    pdf.save()
    return response