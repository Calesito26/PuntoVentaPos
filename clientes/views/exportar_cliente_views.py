import openpyxl

from django.http import HttpResponse

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from clientes.models import Cliente
from usuarios.decorators import administrador_required


@administrador_required
def exportar_clientes_excel(request):
    clientes = Cliente.objects.all().order_by('nombre')

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Clientes'

    hoja.append([
        'Item',
        'Nombre',
        'Tipo documento',
        'Número documento',
        'Teléfono',
        'Correo',
        'Dirección',
        'Municipio',
        'Estado',
    ])

    for index, cliente in enumerate(clientes, start=1):
        hoja.append([
            index,
            cliente.nombre,
            getattr(cliente, 'tipo_documento', ''),
            cliente.numero_documento,
            cliente.telefono or '',
            getattr(cliente, 'correo', '') or getattr(cliente, 'email', ''),
            cliente.direccion or '',
            getattr(cliente, 'municipio', ''),
            'Activo' if getattr(cliente, 'activo', True) else 'Inactivo',
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=clientes.xlsx'

    workbook.save(response)
    return response


@administrador_required
def exportar_clientes_pdf(request):
    clientes = Cliente.objects.all().order_by('nombre')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=clientes.pdf'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y = height - 45

    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(40, y, 'Lista de Clientes')
    y -= 30

    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawString(40, y, 'Item')
    pdf.drawString(75, y, 'Nombre')
    pdf.drawString(230, y, 'Doc')
    pdf.drawString(320, y, 'Telefono')
    pdf.drawString(400, y, 'Correo')
    y -= 16

    pdf.setFont('Helvetica', 8)

    for index, cliente in enumerate(clientes, start=1):
        if y < 50:
            pdf.showPage()
            y = height - 45
            pdf.setFont('Helvetica', 8)

        correo = getattr(cliente, 'correo', '') or getattr(cliente, 'email', '')

        pdf.drawString(40, y, str(index))
        pdf.drawString(75, y, str(cliente.nombre)[:24])
        pdf.drawString(230, y, str(cliente.numero_documento)[:14])
        pdf.drawString(320, y, str(cliente.telefono or '')[:12])
        pdf.drawString(400, y, str(correo)[:24])

        y -= 16

    pdf.save()
    return response