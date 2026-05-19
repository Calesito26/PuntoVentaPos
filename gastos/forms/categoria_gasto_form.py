from django import forms

from gastos.models.categoria_gasto import CategoriaGasto


class CategoriaGastoForm(forms.ModelForm):

    class Meta:
        model = CategoriaGasto

        fields = [
            'nombre',
            'activo'
        ]