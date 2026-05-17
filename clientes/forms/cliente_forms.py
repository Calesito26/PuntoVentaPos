from django import forms

from clientes.models import Cliente


class ClienteForm(forms.ModelForm):

    class Meta:
        model = Cliente

        fields = [
            'tipo_documento',
            'numero_documento',
            'nombre',
            'telefono',
            'email',
            'direccion',
            'activo',
        ]

        labels = {
            'tipo_documento': 'Tipo de documento',
            'numero_documento': 'Número de documento',
            'nombre': 'Nombre del cliente',
            'telefono': 'Teléfono',
            'email': 'Correo electrónico',
            'direccion': 'Dirección',
            'activo': 'Activo',
        }

        widgets = {
            'tipo_documento': forms.Select(
                attrs={
                    'class': 'form-control',
                    'id': 'id_tipo_documento'
                }
            ),
            'numero_documento': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'DNI o RUC',
                    'id': 'id_numero_documento'
                }
            ),
            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre del cliente',
                    'id': 'id_nombre'
                }
            ),
            'telefono': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Opcional'
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Opcional'
                }
            ),
            'direccion': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Opcional: solo si aplica delivery o facturación'
                }
            ),
            'activo': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            ),
        }