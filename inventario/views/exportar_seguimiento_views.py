import openpyxl

from django.db.models import Q
from django.http import HttpResponse

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from inventario.models import StockBodega
from inventario.models import TrasladoBodega
from usuarios.decorators import vendedor_required


def obtener_datos_seguimiento(request):
    buscar = request.GET.get('buscar', '').strip()
    sede_id = request.GET.get('sede', '').strip()

    stocks = StockBodega.objects.select_related(
        'producto',
        'sede'
    ).filter(
        activo=True,
        producto__activo=True
    )

    traslados = TrasladoBodega.objects.select_related(
        'producto',
        'sede_origen',
        'sede_destino',
        'responsable'
    ).all()

    if sede_id:
        stocks = stocks.filter(sede_id=sede_id)
        traslados = traslados.filter(
            Q(sede_origen_id=sede_id) |
            Q(sede_destino_id=sede_id)
        )

    if buscar:
        stocks = stocks.filter(
            Q(producto__nombre__icontains=buscar) |
            Q(producto__codigo__icontains=buscar)
        )

        traslados = traslados.filter(
            Q(producto__nombre__icontains=buscar) |
            Q(producto__codigo__icontains=buscar) |
            Q(codigo__icontains=buscar)
        )

    return stocks, traslados


@vendedor_required
def exportar_seguimiento_excel(request):
    stocks, traslados = obtener_datos_seguimiento(request)

    workbook = openpyxl.Workbook()

    hoja_stock = workbook.active
    hoja_stock.title = 'Stock actual'

    hoja_stock.append([
        'Item',
        'Código de Barra',
        'Producto',
        'Bodega',
        'Stock Actual',
        'Stock Mínimo',
        'Estado',
    ])

    for index, stock in enumerate(stocks, start=1):
        hoja_stock.append([
            index,
            stock.producto.codigo,
            stock.producto.nombre,
            stock.sede.nombre,
            float(stock.stock),
            float(stock.stock_minimo),
            'Activo' if stock.activo else 'Inactivo',
        ])

    hoja_movimientos = workbook.create_sheet('Movimientos')

    hoja_movimientos.append([
        'Item',
        'Fecha y Hora',
        'Código Movimiento',
        'Producto',
        'Origen',
        'Destino',
        'Tipo',
        'Cantidad',
        'Responsable',
        'Observación',
    ])

    for index, traslado in enumerate(traslados, start=1):
        hoja_movimientos.append([
            index,
            traslado.created.strftime('%d/%m/%Y %H:%M'),
            traslado.codigo,
            traslado.producto.nombre,
            traslado.sede_origen.nombre,
            traslado.sede_destino.nombre,
            'Traslado',
            float(traslado.cantidad_traslado),
            traslado.responsable.username if traslado.responsable else '',
            traslado.observacion or '',
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = 'attachment; filename=seguimiento_productos.xlsx'

    workbook.save(response)

    return response


@vendedor_required
def exportar_seguimiento_pdf(request):
    stocks, traslados = obtener_datos_seguimiento(request)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=seguimiento_productos.pdf'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y = height - 40

    pdf.setFont('Helvetica-Bold', 14)
    pdf.drawString(40, y, 'Seguimiento de productos')
    y -= 28

    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawString(40, y, 'Stock actual por bodega')
    y -= 18

    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawString(40, y, 'Item')
    pdf.drawString(70, y, 'Código')
    pdf.drawString(145, y, 'Producto')
    pdf.drawString(330, y, 'Bodega')
    pdf.drawString(430, y, 'Stock')
    pdf.drawString(490, y, 'Mínimo')
    y -= 15

    pdf.setFont('Helvetica', 8)

    for index, stock in enumerate(stocks, start=1):
        if y < 60:
            pdf.showPage()
            y = height - 40
            pdf.setFont('Helvetica', 8)

        pdf.drawString(40, y, str(index))
        pdf.drawString(70, y, stock.producto.codigo[:12])
        pdf.drawString(145, y, stock.producto.nombre[:28])
        pdf.drawString(330, y, stock.sede.nombre[:14])
        pdf.drawString(430, y, str(int(stock.stock)))
        pdf.drawString(490, y, str(int(stock.stock_minimo)))
        y -= 15

    pdf.showPage()
    y = height - 40

    pdf.setFont('Helvetica-Bold', 14)
    pdf.drawString(40, y, 'Historial de movimientos')
    y -= 28

    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawString(40, y, 'Item')
    pdf.drawString(70, y, 'Fecha')
    pdf.drawString(145, y, 'Código')
    pdf.drawString(220, y, 'Producto')
    pdf.drawString(380, y, 'Tipo')
    pdf.drawString(440, y, 'Cantidad')
    y -= 15

    pdf.setFont('Helvetica', 8)

    for index, traslado in enumerate(traslados, start=1):
        if y < 50:
            pdf.showPage()
            y = height - 40
            pdf.setFont('Helvetica', 8)

        pdf.drawString(40, y, str(index))
        pdf.drawString(70, y, traslado.created.strftime('%d/%m/%Y'))
        pdf.drawString(145, y, traslado.codigo[:12])
        pdf.drawString(220, y, traslado.producto.nombre[:24])
        pdf.drawString(380, y, 'Traslado')
        pdf.drawString(440, y, str(int(traslado.cantidad_traslado)))
        y -= 15

    pdf.save()

    return response