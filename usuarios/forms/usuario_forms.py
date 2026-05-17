from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.models import User


class UsuarioSistemaForm(forms.ModelForm):

    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese una contraseña'
            }
        )
    )

    rol = forms.ModelChoiceField(
        label='Rol',
        queryset=Group.objects.filter(
            name__in=[
                'Administrador',
                'Vendedor'
            ]
        ),
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

    class Meta:
        model = User

        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'rol',
            'is_active',
        ]

        labels = {
            'username': 'Usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'is_active': 'Activo',
        }

        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ejemplo: vendedor01'
                }
            ),
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombres'
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Apellidos'
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'correo@ejemplo.com'
                }
            ),
            'is_active': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            ),
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)

        usuario.set_password(
            self.cleaned_data['password']
        )

        if commit:
            usuario.save()

            usuario.groups.clear()

            usuario.groups.add(
                self.cleaned_data['rol']
            )

        return usuario