from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.shortcuts import render
from django.db.models import Q
from inventario.forms import TrasladoBodegaForm
from inventario.models import Sede
from inventario.models import StockBodega
from inventario.models import TrasladoBodega
from usuarios.decorators import administrador_required


@administrador_required
def traslado_list(request):
    sede_id = request.GET.get('sede', '')
    buscar = request.GET.get('buscar', '').strip()

    sedes = Sede.objects.filter(activo=True).order_by('nombre')

    traslados = TrasladoBodega.objects.select_related(
        'sede_origen',
        'sede_destino',
        'producto',
        'responsable'
    ).all()

    if sede_id:
        traslados = traslados.filter(sede_origen_id=sede_id)

    if buscar:
        traslados = traslados.filter(Q(producto__nombre__icontains=buscar) | Q(producto__codigo__icontains=buscar) | Q(codigo__icontains=buscar))

    return render(
        request,
        'inventario/traslado_list.html',
        {
            'traslados': traslados,
            'sedes': sedes,
            'sede_id': sede_id,
            'buscar': buscar,
        }
    )


@administrador_required
@transaction.atomic
def traslado_create(request):
    form = TrasladoBodegaForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            sede_origen = form.cleaned_data['sede_origen']
            sede_destino = form.cleaned_data['sede_destino']
            producto = form.cleaned_data['producto']
            cantidad = form.cleaned_data['cantidad_traslado']

            if sede_origen == sede_destino:
                messages.error(
                    request,
                    'La bodega origen y destino no pueden ser iguales.'
                )
                return redirect('inventario:traslado_create')

            stock_origen = StockBodega.objects.filter(
                sede=sede_origen,
                producto=producto,
                activo=True
            ).first()

            if not stock_origen:
                messages.error(
                    request,
                    'El producto no tiene stock registrado en la bodega origen.'
                )
                return redirect('inventario:traslado_create')

            if stock_origen.stock < cantidad:
                messages.error(
                    request,
                    'No hay stock suficiente para realizar el traslado.'
                )
                return redirect('inventario:traslado_create')

            stock_destino, creado = StockBodega.objects.get_or_create(
                sede=sede_destino,
                producto=producto,
                defaults={
                    'stock': Decimal('0.00'),
                    'stock_minimo': stock_origen.stock_minimo,
                    'activo': True,
                }
            )

            cantidad_actual = stock_origen.stock

            stock_origen.stock = stock_origen.stock - cantidad
            stock_origen.save()

            stock_destino.stock = stock_destino.stock + cantidad
            stock_destino.save()

            traslado = form.save(commit=False)
            traslado.cantidad_actual = cantidad_actual
            traslado.cantidad_final = stock_origen.stock
            traslado.valor_traslado = cantidad * producto.precio_compra
            traslado.responsable = request.user
            traslado.estado = 'REALIZADO'
            traslado.save()

            messages.success(
                request,
                'Traslado realizado correctamente.'
            )

            return redirect('inventario:traslado_list')

    return render(
        request,
        'inventario/traslado_form.html',
        {
            'form': form,
            'titulo': 'Nuevo traslado'
        }
    )