import json

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from gastos.models.gasto import Gasto


def gasto_fijo_list(request):
    gastos_fijos = Gasto.objects.filter(
        es_fijo=True
    ).select_related(
        'categoria',
        'proveedor'
    ).order_by('-id')

    total_gastos = sum(
        gasto.valor for gasto in gastos_fijos if gasto.pagar_fijo
    )

    return render(
        request,
        'gastos/gasto_fijo_list.html',
        {
            'gastos_fijos': gastos_fijos,
            'total_gastos': total_gastos,
        }
    )


def marcar_gasto_fijo_ajax(request, gasto_id):
    gasto = get_object_or_404(Gasto, id=gasto_id)

    gasto.es_fijo = not gasto.es_fijo
    gasto.pagar_fijo = gasto.es_fijo
    gasto.sacar_caja_fijo = gasto.sacar_caja
    gasto.fecha_aplicacion = timezone.now().date()
    gasto.save()

    return JsonResponse({
        'ok': True,
        'es_fijo': gasto.es_fijo,
        'mensaje': 'Gasto fijo actualizado.'
    })


def actualizar_gasto_fijo_ajax(request, gasto_id):
    if request.method != 'POST':
        return JsonResponse({
            'ok': False,
            'mensaje': 'Método no permitido.'
        })

    data = json.loads(request.body)

    gasto = get_object_or_404(
        Gasto,
        id=gasto_id,
        es_fijo=True
    )

    gasto.pagar_fijo = data.get('pagar_fijo', False)
    gasto.sacar_caja_fijo = data.get('sacar_caja_fijo', False)
    gasto.save()

    return JsonResponse({
        'ok': True
    })


def aplicar_gastos_fijos(request):
    if request.method != 'POST':
        return JsonResponse({
            'ok': False,
            'mensaje': 'Método no permitido.'
        })

    gastos = Gasto.objects.filter(
        es_fijo=True,
        pagar_fijo=True
    )

    if not gastos.exists():
        return JsonResponse({
            'ok': False,
            'mensaje': 'Seleccione al menos un gasto fijo para pagar.'
        })

    total = 0

    for gasto in gastos:
        Gasto.objects.create(
            descripcion=gasto.descripcion,
            categoria=gasto.categoria,
            proveedor=gasto.proveedor,
            responsable=request.user,
            metodo_pago=gasto.metodo_pago,
            tipo_gasto=gasto.tipo_gasto,
            valor=gasto.valor,
            sacar_caja=gasto.sacar_caja_fijo,
            estado='PROCESADO',
            es_fijo=False
        )

        total += gasto.valor

    return JsonResponse({
        'ok': True,
        'mensaje': f'Gastos fijos aplicados correctamente. Total: S/ {total}'
    })