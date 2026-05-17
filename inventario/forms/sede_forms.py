from django import forms

from inventario.models import Sede


class SedeForm(forms.ModelForm):

    class Meta:
        model = Sede

        fields = [
            'nombre',
            'direccion',
            'descripcion',
            'activo',
        ]

        labels = {
            'nombre': 'Nombre',
            'direccion': 'Dirección',
            'descripcion': 'Descripción',
            'activo': 'Activo',
        }

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }