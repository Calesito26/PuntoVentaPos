from django import forms

from inventario.models import ConfiguracionEmpresa


class ConfiguracionEmpresaForm(forms.ModelForm):

    class Meta:
        model = ConfiguracionEmpresa

        fields = [
            'nombre_empresa',
            'razon_social',
            'ruc',
            'direccion',
            'telefono',
            'email',
            'pagina_web',
            'logo',
            'logo_sidebar',
            'pie_ticket',
            'smtp_email',
            'smtp_password',
        ]

        widgets = {
            'nombre_empresa': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'razon_social': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'ruc': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'direccion': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'telefono': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'email': forms.EmailInput(
                attrs={'class': 'form-control'}
            ),

            'pagina_web': forms.URLInput(
                attrs={'class': 'form-control'}
            ),

            'pie_ticket': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3
                }
            ),

            'smtp_email': forms.EmailInput(
                attrs={'class': 'form-control'}
            ),

            'smtp_password': forms.PasswordInput(
                attrs={
                    'class': 'form-control'
                },
                render_value=True
            ),
        }