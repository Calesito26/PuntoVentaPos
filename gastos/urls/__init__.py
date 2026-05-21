from django.urls import path, include

app_name = 'gastos'

urlpatterns = [
    path('categorias/', include('gastos.urls.categoria_gasto_urls')),
    path('egresos/', include('gastos.urls.gasto_urls')),
    path('fijos/',include('gastos.urls.gasto_fijo_urls')),
    path('categorias-reporte/',include('gastos.urls.gasto_categoria_urls')
),
]