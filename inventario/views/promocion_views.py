from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from inventario.forms import PromocionForm
from inventario.models import Promocion
from usuarios.decorators import administrador_required


@administrador_required
def promocion_list(request):
    buscar = request.GET.get('buscar', '').strip()
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    promociones = Promocion.objects.select_related(
        'responsable'
    ).all()

    if buscar:
        promociones = promociones.filter(
            Q(nombre__icontains=buscar) |
            Q(responsable__username__icontains=buscar)
        )

    if fecha_inicio:
        promociones = promociones.filter(
            fecha_inicio__date__gte=fecha_inicio
        )

    if fecha_fin:
        promociones = promociones.filter(
            fecha_fin__date__lte=fecha_fin
        )

    return render(
        request,
        'inventario/promocion_list.html',
        {
            'promociones': promociones,
            'buscar': buscar,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
        }
    )


@administrador_required
def promocion_create(request):
    form = PromocionForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            promocion = form.save(commit=False)
            promocion.responsable = request.user
            promocion.save()

            messages.success(
                request,
                'Promoción creada correctamente.'
            )

            return redirect('inventario:promocion_list')

    return render(
        request,
        'inventario/promocion_form.html',
        {
            'form': form,
            'titulo': 'Nueva Promoción'
        }
    )


@administrador_required
def promocion_update(request, pk):
    promocion = get_object_or_404(
        Promocion,
        pk=pk
    )

    form = PromocionForm(
        request.POST or None,
        instance=promocion
    )

    if request.method == 'POST':
        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Promoción actualizada correctamente.'
            )

            return redirect('inventario:promocion_list')

    return render(
        request,
        'inventario/promocion_form.html',
        {
            'form': form,
            'titulo': 'Editar Promoción'
        }
    )