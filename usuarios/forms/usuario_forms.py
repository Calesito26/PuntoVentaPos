from django import forms
from django.contrib.auth.models import User, Group

from inventario.models import Sede
from usuarios.models import UsuarioSede, UsuarioPerfil


class UsuarioSistemaForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )

    rol = forms.ModelChoiceField(
        label='Cargo',
        queryset=Group.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    sede = forms.ModelChoiceField(
        label='Sucursal asignada',
        queryset=Sede.objects.filter(activo=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )

    tipo_documento = forms.ChoiceField(
        label='Tipo de documento',
        choices=UsuarioPerfil.TIPO_DOCUMENTO,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    numero_documento = forms.CharField(
        label='Número de documento',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    direccion = forms.CharField(
        label='Dirección',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    telefono = forms.CharField(
        label='Teléfono',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'email',
            'password',
            'is_active',
        ]

        labels = {
            'username': 'Usuario',
            'first_name': 'Nombre completo',
            'email': 'Correo electrónico',
            'is_active': 'Activo',
        }

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        usuario = self.instance

        if usuario and usuario.pk:
            grupo = usuario.groups.first()

            if grupo:
                self.fields['rol'].initial = grupo

            usuario_sede = UsuarioSede.objects.filter(
                usuario=usuario
            ).first()

            if usuario_sede:
                self.fields['sede'].initial = usuario_sede.sede

            perfil = UsuarioPerfil.objects.filter(
                usuario=usuario
            ).first()

            if perfil:
                self.fields['tipo_documento'].initial = perfil.tipo_documento
                self.fields['numero_documento'].initial = perfil.numero_documento
                self.fields['direccion'].initial = perfil.direccion
                self.fields['telefono'].initial = perfil.telefono

    def save(self, commit=True):
        usuario = super().save(commit=False)

        password = self.cleaned_data.get('password')

        if password:
            usuario.set_password(password)

        if commit:
            usuario.save()

            rol = self.cleaned_data.get('rol')
            sede = self.cleaned_data.get('sede')

            usuario.groups.clear()

            if rol:
                usuario.groups.add(rol)

            if rol and rol.name.lower() == 'vendedor':
                if sede:
                    UsuarioSede.objects.update_or_create(
                        usuario=usuario,
                        defaults={
                            'sede': sede
                        }
                    )
            else:
                UsuarioSede.objects.filter(
                    usuario=usuario
                ).delete()

            perfil, created = UsuarioPerfil.objects.get_or_create(
                usuario=usuario
            )

            perfil.tipo_documento = self.cleaned_data.get(
                'tipo_documento'
            )

            perfil.numero_documento = self.cleaned_data.get(
                'numero_documento'
            )

            perfil.direccion = self.cleaned_data.get(
                'direccion'
            )

            perfil.telefono = self.cleaned_data.get(
                'telefono'
            )

            perfil.save()

        return usuario