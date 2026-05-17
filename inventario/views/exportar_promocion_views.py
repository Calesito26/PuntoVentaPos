import openpyxl

from django.http import HttpResponse

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from inventario.models import Promocion
from usuarios.decorators import administrador_required


def obtener_promociones_exportar():
    return Promocion.objects.select_related(
        'responsable'
    ).all().order_by('-fecha_inicio')


@administrador_required
def exportar_promociones_excel(request):
    promociones = obtener_promociones_exportar()

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Promociones'

    hoja.append([
        'Item',
        'Nombre',
        'Fecha inicio',
        'Fecha fin',
        'Descuento',
        'Responsable',
        'Estado',
    ])

    for index, promocion in enumerate(promociones, start=1):
        hoja.append([
            index,
            promocion.nombre,
            promocion.fecha_inicio.strftime('%d/%m/%Y %H:%M'),
            promocion.fecha_fin.strftime('%d/%m/%Y %H:%M'),
            float(promocion.porcentaje_descuento),
            promocion.responsable.username if promocion.responsable else '',
            'Activo' if promocion.activo else 'Inactivo',
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=promociones.xlsx'

    workbook.save(response)

    return response


@administrador_required
def exportar_promociones_pdf(request):
    promociones = obtener_promociones_exportar()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=promociones.pdf'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y = height - 40

    pdf.setFont('Helvetica-Bold', 14)
    pdf.drawString(40, y, 'Historial de promociones')
    y -= 30

    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawString(40, y, 'Item')
    pdf.drawString(70, y, 'Nombre')
    pdf.drawString(220, y, 'Inicio')
    pdf.drawString(320, y, 'Fin')
    pdf.drawString(420, y, 'Desc.')
    pdf.drawString(470, y, 'Estado')
    y -= 15

    pdf.setFont('Helvetica', 8)

    for index, promocion in enumerate(promociones, start=1):

        if y < 50:
            pdf.showPage()
            y = height - 40
            pdf.setFont('Helvetica', 8)

        pdf.drawString(40, y, str(index))
        pdf.drawString(70, y, promocion.nombre[:22])
        pdf.drawString(220, y, promocion.fecha_inicio.strftime('%d/%m/%Y'))
        pdf.drawString(320, y, promocion.fecha_fin.strftime('%d/%m/%Y'))
        pdf.drawString(420, y, f'{promocion.porcentaje_descuento}%')
        pdf.drawString(470, y, 'Activo' if promocion.activo else 'Inactivo')

        y -= 15

    pdf.save()

    return response