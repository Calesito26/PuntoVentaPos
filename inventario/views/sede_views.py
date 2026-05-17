from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from inventario.forms import SedeForm
from inventario.models import Sede
from usuarios.decorators import administrador_required


@administrador_required
def sede_list(request):
    sedes = Sede.objects.all().order_by('id')

    return render(
        request,
        'inventario/sede_list.html',
        {
            'sedes': sedes
        }
    )


@administrador_required
def sede_create(request):
    form = SedeForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('inventario:sede_list')

    return render(
        request,
        'inventario/sede_form.html',
        {
            'form': form,
            'titulo': 'Nueva Bodega'
        }
    )


@administrador_required
def sede_update(request, pk):
    sede = get_object_or_404(Sede, pk=pk)

    form = SedeForm(
        request.POST or None,
        instance=sede
    )

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('inventario:sede_list')

    return render(
        request,
        'inventario/sede_form.html',
        {
            'form': form,
            'titulo': 'Editar Bodega'
        }
    )


@administrador_required
def sede_delete(request, pk):
    sede = get_object_or_404(Sede, pk=pk)
    sede.delete()

    return redirect('inventario:sede_list')