from django.shortcuts import render, get_object_or_404, redirect

from gastos.models.categoria_gasto import CategoriaGasto
from gastos.forms.categoria_gasto_form import CategoriaGastoForm
import openpyxl

from django.http import HttpResponse

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def categoria_gasto_list(request):
    buscar = request.GET.get('buscar', '').strip()
    editar_id = request.GET.get('editar')
    nueva = request.GET.get('nuevo')

    categorias = CategoriaGasto.objects.all().order_by('nombre')

    if buscar:
        categorias = categorias.filter(nombre__icontains=buscar)

    form = None
    categoria_editar = None

    if editar_id:
        categoria_editar = get_object_or_404(CategoriaGasto, id=editar_id)
        form = CategoriaGastoForm(instance=categoria_editar)

    elif nueva:
        form = CategoriaGastoForm()

    return render(
        request,
        'gastos/categoria_gasto_list.html',
        {
            'categorias': categorias,
            'buscar': buscar,
            'form': form,
            'categoria_editar': categoria_editar,
            'mostrar_modal': True if form else False,
        }
    )


def categoria_gasto_save(request):
    categoria_id = request.POST.get('categoria_id')

    if categoria_id:
        categoria = get_object_or_404(CategoriaGasto, id=categoria_id)
        form = CategoriaGastoForm(request.POST, instance=categoria)
    else:
        form = CategoriaGastoForm(request.POST)

    if form.is_valid():
        form.save()

    return redirect('gastos:categoria_gasto_list')


def categoria_gasto_delete(request, pk):
    categoria = get_object_or_404(CategoriaGasto, pk=pk)
    categoria.delete()

    return redirect('gastos:categoria_gasto_list')

def categoria_gasto_excel(request):
    categorias = CategoriaGasto.objects.all().order_by('nombre')

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Categorias Gastos'

    hoja.append([
        'Item',
        'Nombre',
        'Estado',
    ])

    for index, categoria in enumerate(categorias, start=1):
        hoja.append([
            index,
            categoria.nombre,
            'ACTIVO' if categoria.activo else 'INACTIVO',
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=categorias_gastos.xlsx'

    workbook.save(response)
    return response


def categoria_gasto_pdf(request):
    categorias = CategoriaGasto.objects.all().order_by('nombre')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=categorias_gastos.pdf'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y = height - 50

    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(40, y, 'Categorias de Gastos')
    y -= 35

    pdf.setFont('Helvetica-Bold', 9)
    pdf.drawString(40, y, 'Item')
    pdf.drawString(90, y, 'Nombre')
    pdf.drawString(320, y, 'Estado')
    y -= 18

    pdf.setFont('Helvetica', 9)

    for index, categoria in enumerate(categorias, start=1):
        if y < 50:
            pdf.showPage()
            y = height - 50
            pdf.setFont('Helvetica', 9)

        pdf.drawString(40, y, str(index))
        pdf.drawString(90, y, categoria.nombre)
        pdf.drawString(320, y, 'ACTIVO' if categoria.activo else 'INACTIVO')

        y -= 18

    pdf.save()
    return response