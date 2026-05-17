from django import forms

from productos.models import Producto


class ProductoForm(forms.ModelForm):

    class Meta:
        model = Producto

        fields = [
            'nombre',
            'categoria',
            'descripcion',
            'precio_compra',
            'precio_venta',
            'stock',
            'imagen',
            'activo',
        ]

        widgets = {
            
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del producto'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del producto'
            }),
            'precio_compra': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'precio_venta': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }