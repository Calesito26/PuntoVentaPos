import openpyxl

from django.http import HttpResponse

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from inventario.models import TrasladoBodega
from usuarios.decorators import administrador_required


@administrador_required
def exportar_traslado_excel(request):

    traslados = TrasladoBodega.objects.select_related(
        'sede_origen',
        'sede_destino',
        'producto',
        'responsable'
    )

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Traslados'

    hoja.append([
        'Código',
        'Fecha',
        'Origen',
        'Destino',
        'Producto',
        'Cantidad',
        'Valor',
        'Responsable',
        'Estado',
    ])

    for traslado in traslados:
        hoja.append([
            traslado.codigo,
            traslado.created.strftime('%d/%m/%Y %H:%M'),
            traslado.sede_origen.nombre,
            traslado.sede_destino.nombre,
            traslado.producto.nombre,
            float(traslado.cantidad_traslado),
            float(traslado.valor_traslado),
            str(traslado.responsable),
            traslado.estado,
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename=traslados.xlsx'

    workbook.save(response)

    return response


@administrador_required
def exportar_traslado_pdf(request):

    traslados = TrasladoBodega.objects.select_related(
        'sede_origen',
        'sede_destino',
        'producto'
    )

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename=traslados.pdf'

    pdf = canvas.Canvas(
        response,
        pagesize=letter
    )

    width, height = letter

    y = height - 40

    pdf.setFont('Helvetica-Bold', 14)
    pdf.drawString(
        40,
        y,
        'Historial de traslados'
    )

    y -= 30

    pdf.setFont('Helvetica-Bold', 8)

    pdf.drawString(40, y, 'Cod')
    pdf.drawString(90, y, 'Producto')
    pdf.drawString(230, y, 'Origen')
    pdf.drawString(320, y, 'Destino')
    pdf.drawString(420, y, 'Cantidad')

    y -= 15

    pdf.setFont('Helvetica', 8)

    for traslado in traslados:

        if y < 50:
            pdf.showPage()
            y = height - 40

        pdf.drawString(
            40,
            y,
            traslado.codigo
        )

        pdf.drawString(
            90,
            y,
            traslado.producto.nombre[:22]
        )

        pdf.drawString(
            230,
            y,
            traslado.sede_origen.nombre[:12]
        )

        pdf.drawString(
            320,
            y,
            traslado.sede_destino.nombre[:12]
        )

        pdf.drawString(
            420,
            y,
            str(
                int(
                    traslado.cantidad_traslado
                )
            )
        )

        y -= 15

    pdf.save()

    return response