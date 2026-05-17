from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.shortcuts import render

from usuarios.decorators import administrador_required
from usuarios.forms import UsuarioSistemaForm


@administrador_required
def usuario_list(request):
    usuarios = User.objects.all().order_by(
        'username'
    )

    return render(
        request,
        'usuarios/usuario_list.html',
        {
            'usuarios': usuarios
        }
    )


@administrador_required
def usuario_create(request):
    form = UsuarioSistemaForm(
        request.POST or None
    )

    if request.method == 'POST':
        if form.is_valid():
            form.save()

            return redirect(
                'usuarios:usuario_list'
            )

    return render(
        request,
        'usuarios/usuario_form.html',
        {
            'form': form,
            'titulo': 'Registrar usuario del sistema'
        }
    )