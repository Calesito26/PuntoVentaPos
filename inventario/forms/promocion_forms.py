from django import forms

from inventario.models import Promocion


class PromocionForm(forms.ModelForm):

    class Meta:
        model = Promocion

        fields = [
            'nombre',
            'fecha_inicio',
            'fecha_fin',
            'porcentaje_descuento',
            'activo',
        ]

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Nombre de la promoción'
            }),
            'fecha_inicio': forms.DateTimeInput(attrs={
                'class': 'form-control form-control-sm',
                'type': 'datetime-local'
            }),
            'fecha_fin': forms.DateTimeInput(attrs={
                'class': 'form-control form-control-sm',
                'type': 'datetime-local'
            }),
            'porcentaje_descuento': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }