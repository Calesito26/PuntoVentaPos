from django.shortcuts import render, get_object_or_404

from clientes.models.cliente import Cliente
from ventas.models.venta import Venta


def cliente_detalle(request, cliente_id):

    cliente = get_object_or_404(
        Cliente,
        id=cliente_id
    )

    ventas = Venta.objects.filter(
        cliente=cliente
    ).order_by('-created')

    resumen_metodos = {}

    for venta in ventas:

        metodo = venta.metodo_pago or 'EFECTIVO'

        if metodo not in resumen_metodos:
            resumen_metodos[metodo] = {
                'total': 0,
                'devoluciones': 0,
                'creditos': 0,
                'debitos': 0
            }

        resumen_metodos[metodo]['total'] += venta.total

    return render(
        request,
        'clientes/cliente_detalle.html',
        {
            'cliente': cliente,
            'ventas': ventas,
            'resumen_metodos': resumen_metodos
        }
    )