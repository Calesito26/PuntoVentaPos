from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from clientes.models import Cliente


def eliminar_cliente(request, cliente_id):
    cliente = get_object_or_404(
        Cliente,
        id=cliente_id
    )

    cliente.delete()

    return JsonResponse({
        'ok': True
    })