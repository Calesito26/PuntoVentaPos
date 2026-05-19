from django.urls import path, include

app_name = 'gastos'


urlpatterns = [

    path(
        'categorias/',
        include(
            'gastos.urls.categoria_gasto_urls'
        )
    ),
]