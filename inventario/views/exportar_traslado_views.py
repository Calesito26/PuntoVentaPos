import openpyxl

from django.http import HttpResponse

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from inventario.models import (
    TrasladoBodega,
    ConfiguracionEmpresa
)

from usuarios.decorators import (
    administrador_required
)


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
            traslado.created.strftime(
                '%d/%m/%Y %H:%M'
            ),
            traslado.sede_origen.nombre,
            traslado.sede_destino.nombre,
            traslado.producto.nombre,
            float(
                traslado.cantidad_traslado
            ),
            float(
                traslado.valor_traslado
            ),
            str(
                traslado.responsable
            ),
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

    traslados = (
        TrasladoBodega.objects
        .select_related(
            'sede_origen',
            'sede_destino',
            'producto'
        )
    )

    empresa = (
        ConfiguracionEmpresa
        .obtener_configuracion()
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

    y = height - 45

    # ==================
    # CABECERA EMPRESA
    # ==================

    if empresa.logo:
        try:
            pdf.drawImage(
                empresa.logo.path,
                40,
                y - 50,
                width=70,
                height=50,
                preserveAspectRatio=True,
                mask='auto'
            )
        except Exception:
            pass

    pdf.setFont(
        'Helvetica-Bold',
        16
    )

    pdf.drawString(
        125,
        y,
        empresa.nombre_empresa
        or
        'PuntoVentaPOS'
    )

    y -= 18

    pdf.setFont(
        'Helvetica',
        9
    )

    if empresa.ruc:
        pdf.drawString(
            125,
            y,
            f'RUC: {empresa.ruc}'
        )
        y -= 13

    if empresa.direccion:
        pdf.drawString(
            125,
            y,
            f'Dirección: {empresa.direccion}'
        )
        y -= 13

    if empresa.telefono:
        pdf.drawString(
            125,
            y,
            f'Teléfono: {empresa.telefono}'
        )
        y -= 13

    if empresa.email:
        pdf.drawString(
            125,
            y,
            f'Correo: {empresa.email}'
        )
        y -= 13

    y -= 20

    # ==================
    # TITULO REPORTE
    # ==================

    pdf.setFont(
        'Helvetica-Bold',
        15
    )

    pdf.drawString(
        40,
        y,
        'Historial de Traslados'
    )

    y -= 28

    # ==================
    # CABECERA TABLA
    # ==================

    pdf.setFont(
        'Helvetica-Bold',
        8
    )

    pdf.drawString(40, y, 'Cod')
    pdf.drawString(90, y, 'Producto')
    pdf.drawString(230, y, 'Origen')
    pdf.drawString(320, y, 'Destino')
    pdf.drawString(420, y, 'Cantidad')

    y -= 16

    pdf.setFont(
        'Helvetica',
        8
    )

    # ==================
    # DETALLE
    # ==================

    for traslado in traslados:

        if y < 50:

            pdf.showPage()

            y = height - 45

            pdf.setFont(
                'Helvetica-Bold',
                15
            )

            pdf.drawString(
                40,
                y,
                'Historial de Traslados'
            )

            y -= 28

            pdf.setFont(
                'Helvetica-Bold',
                8
            )

            pdf.drawString(40, y, 'Cod')
            pdf.drawString(90, y, 'Producto')
            pdf.drawString(230, y, 'Origen')
            pdf.drawString(320, y, 'Destino')
            pdf.drawString(420, y, 'Cantidad')

            y -= 16

            pdf.setFont(
                'Helvetica',
                8
            )

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