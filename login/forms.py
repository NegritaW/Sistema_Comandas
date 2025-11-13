from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
import re


class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'nombre_completo', 'email', 'rol']
        labels = {
            'username': 'Nombre de usuario',
            'nombre_completo': 'Nombre completo',
            'email': 'Correo electrónico',
            'rol': 'Rol',
        }
        error_messages = {
            'username': {
                'required': 'El nombre de usuario es obligatorio.',
                'unique': 'Ya existe una cuenta con este nombre de usuario.',
            },
            'email': {
                'required': 'El correo electrónico es obligatorio.',
                'invalid': 'Ingresa un correo electrónico válido (debe contener @ y un dominio).',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Traducción de labels de las contraseñas
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Repetir contraseña'

        # Placeholders lindos
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Ingresa una contraseña segura'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Repite la contraseña'
        })

        # Limpiar textos de ayuda
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

        # Errores traducidos
        self.fields['password1'].error_messages = {
            'required': 'Debes ingresar una contraseña.',
        }
        self.fields['password2'].error_messages = {
            'required': 'Debes repetir la contraseña.',
            'password_mismatch': 'Las contraseñas no coinciden.',
        }

    # VALIDACIÓN COMPLETA DE CONTRASEÑA EN ESPAÑOL
    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        username = self.cleaned_data.get("username", "")

        if not password:
            raise forms.ValidationError("Debes ingresar una contraseña.")

        #  Largo mínimo
        if len(password) < 8:
            raise forms.ValidationError("La contraseña es demasiado corta. Debe tener al menos 8 caracteres.")

        #  No similar al username
        if username.lower() in password.lower():
            raise forms.ValidationError("La contraseña no puede ser demasiado similar al nombre de usuario.")

        #  Debe contener letras y números
        if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
            raise forms.ValidationError("La contraseña debe contener letras y números.")

        #  Debe incluir minúsculas y mayúsculas
        if not re.search(r"[a-z]", password) or not re.search(r"[A-Z]", password):
            raise forms.ValidationError("La contraseña debe incluir al menos una letra minúscula y una mayúscula.")

        #  No común
        comunes = ["12345678", "password", "qwerty", "abc123", "contraseña"]
        if password.lower() in comunes:
            raise forms.ValidationError("La contraseña es demasiado común. Usa algo más seguro.")

        #  No solo números
        if password.isdigit():
            raise forms.ValidationError("La contraseña no puede ser completamente numérica.")

        #  No espacios
        if " " in password:
            raise forms.ValidationError("La contraseña no puede contener espacios.")

        return password