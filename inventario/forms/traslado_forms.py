from django import forms

from inventario.models import Sede
from inventario.models import TrasladoBodega
from productos.models import Producto


class TrasladoBodegaForm(forms.ModelForm):

    class Meta:
        model = TrasladoBodega

        fields = [
            'sede_origen',
            'sede_destino',
            'producto',
            'cantidad_traslado',
            'observacion',
        ]

        labels = {
            'sede_origen': 'Bodega origen',
            'sede_destino': 'Bodega destino',
            'producto': 'Producto',
            'cantidad_traslado': 'Cantidad a trasladar',
            'observacion': 'Observación',
        }

        widgets = {
            'sede_origen': forms.Select(attrs={
                'class': 'form-control form-control-sm'
            }),
            'sede_destino': forms.Select(attrs={
                'class': 'form-control form-control-sm'
            }),
            'producto': forms.Select(attrs={
                'class': 'form-control form-control-sm'
            }),
            'cantidad_traslado': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'step': '0.01',
                'min': '0.01'
            }),
            'observacion': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['sede_origen'].queryset = Sede.objects.filter(
            activo=True
        ).order_by('nombre')

        self.fields['sede_destino'].queryset = Sede.objects.filter(
            activo=True
        ).order_by('nombre')

        self.fields['producto'].queryset = Producto.objects.filter(
            activo=True
        ).order_by('nombre')