from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth import views as auth_views
from core.views.home import home
from django.urls import path, include

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('productos/', include('productos.urls.producto_urls')),
    path('ventas/', include('ventas.urls.venta_urls')),
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'),name='login'),
    path('logout/',auth_views.LogoutView.as_view(),name='logout'),
    path('usuarios/', include('usuarios.urls.usuario_urls')),
    path('clientes/', include('clientes.urls.cliente_urls')),
    path('login/',auth_views.LoginView.as_view(template_name='usuarios/login.html'),name='login'),
    path('logout/',auth_views.LogoutView.as_view(),name='logout'),
    path('password-change/',auth_views.PasswordChangeView.as_view(template_name='usuarios/password_change.html'),name='password_change'),
    path('password-change/done/',auth_views.PasswordChangeDoneView.as_view(template_name='usuarios/password_change_done.html'),name='password_change_done'),
    path('inventario/', include('inventario.urls.sede_urls')),
    path('compras/', include('compras.urls.compra_urls')),
    path('gastos/',include('gastos.urls')),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )