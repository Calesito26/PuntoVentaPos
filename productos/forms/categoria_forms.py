from django import forms

from productos.models import Categoria


class CategoriaForm(forms.ModelForm):

    class Meta:
        model = Categoria

        fields = [
            'nombre',
            'activo',
        ]

        labels = {
            'nombre': 'Nombre de la categoría',
            'activo': 'Activo',
        }

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Nombre de la categoría'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }