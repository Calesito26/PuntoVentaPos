from django.contrib.auth.decorators import user_passes_test


def administrador_required(view_func):
    return user_passes_test(
        lambda user: user.is_authenticated and (
            user.is_superuser
            or user.groups.filter(name='Administrador').exists()
        ),
        login_url='login'
    )(view_func)


def vendedor_required(view_func):
    return user_passes_test(
        lambda user: user.is_authenticated and (
            user.is_superuser
            or user.groups.filter(name='Administrador').exists()
            or user.groups.filter(name='Vendedor').exists()
        ),
        login_url='login'
    )(view_func)