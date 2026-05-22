from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.utils import timezone

from inventario.models import ConfiguracionEmpresa
from usuarios.forms import LoginForm
from usuarios.models import LoginAttempt


def obtener_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')

    if forwarded:
        return forwarded.split(',')[0]

    return request.META.get('REMOTE_ADDR')


def login_view(request):
    empresa = ConfiguracionEmpresa.obtener_configuracion()

    form = LoginForm(
        request.POST or None
    )

    if request.method == 'POST':

        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            ip = obtener_ip(request)

            intento, _ = LoginAttempt.objects.get_or_create(
                username=username,
                ip_address=ip
            )

            if intento.esta_bloqueado():

                restante = int(
                    (
                        intento.bloqueado_hasta
                        -
                        timezone.now()
                    ).total_seconds() / 60
                )

                messages.error(
                    request,
                    f'Acceso bloqueado. Intente nuevamente en {restante} minutos.'
                )

            else:

                usuario = authenticate(
                    request,
                    username=username,
                    password=password
                )

                if usuario is not None:

                    intento.reiniciar()

                    login(
                        request,
                        usuario
                    )

                    return redirect('home')

                intento.intentos += 1

                if intento.intentos >= 3:

                    intento.bloquear()

                    messages.error(
                        request,
                        'Demasiados intentos fallidos. Acceso bloqueado por 30 minutos.'
                    )

                else:

                    intento.save()

                    messages.error(
                        request,
                        f'Usuario o contraseña incorrectos. Intentos restantes: {3 - intento.intentos}.'
                    )

        else:

            messages.error(
                request,
                'Complete correctamente el CAPTCHA.'
            )

    return render(
        request,
        'usuarios/login.html',
        {
            'form': form,
            'empresa': empresa
        }
    )