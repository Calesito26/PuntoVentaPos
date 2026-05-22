import openpyxl

from django.db.models import Q
from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from inventario.models import ConfiguracionEmpresa, StockBodega, TrasladoBodega
from core.services.pdf_empresa_service import agregar_cabecera_empresa
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

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    elementos = []

    empresa = ConfiguracionEmpresa.obtener_configuracion()

    agregar_cabecera_empresa(
        elementos,
        empresa,
        'Seguimiento de Productos'
    )

    # --- Sección: Stock actual por bodega ---
    elementos.append(Paragraph('Stock actual por bodega', styles['Heading2']))
    elementos.append(Spacer(1, 6))

    data_stock = [[
        'Item',
        'Código',
        'Producto',
        'Bodega',
        'Stock',
        'Mínimo',
    ]]

    for index, stock in enumerate(stocks, start=1):
        data_stock.append([
            str(index),
            stock.producto.codigo,
            stock.producto.nombre,
            stock.sede.nombre,
            str(int(stock.stock)),
            str(int(stock.stock_minimo)),
        ])

    tabla_stock = Table(
        data_stock,
        colWidths=[30, 75, 180, 120, 50, 55]
    )

    tabla_stock.setStyle(TableStyle([
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0),  10),
        ('TOPPADDING',    (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.black),
    ]))

    elementos.append(tabla_stock)
    elementos.append(Spacer(1, 20))

    # --- Sección: Historial de movimientos ---
    elementos.append(Paragraph('Historial de movimientos', styles['Heading2']))
    elementos.append(Spacer(1, 6))

    data_traslados = [[
        'Item',
        'Fecha',
        'Código',
        'Producto',
        'Tipo',
        'Cantidad',
    ]]

    for index, traslado in enumerate(traslados, start=1):
        data_traslados.append([
            str(index),
            traslado.created.strftime('%d/%m/%Y'),
            traslado.codigo,
            traslado.producto.nombre,
            'Traslado',
            str(int(traslado.cantidad_traslado)),
        ])

    tabla_traslados = Table(
        data_traslados,
        colWidths=[30, 70, 80, 200, 60, 60]
    )

    tabla_traslados.setStyle(TableStyle([
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0),  10),
        ('TOPPADDING',    (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.black),
    ]))

    elementos.append(tabla_traslados)

    doc.build(elementos)

    return response