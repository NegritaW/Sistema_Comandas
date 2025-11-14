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
                'invalid': 'Ingresa un correo electrónico válido.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Etiquetas bonitas
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Repetir contraseña'

        # Placeholders
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Ingresa una contraseña segura'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Repite la contraseña'
        })

        # Sin textos de ayuda
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''


    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        username = self.cleaned_data.get("username", "")
        email = self.cleaned_data.get("email", "")

        if not password:
            raise forms.ValidationError("Debes ingresar una contraseña.")

        # Largo mínimo
        if len(password) < 8:
            raise forms.ValidationError("Debe tener al menos 8 caracteres.")

        # No similar al username
        if username and username.lower() in password.lower():
            raise forms.ValidationError(
                "La contraseña no puede ser similar al nombre de usuario."
            )

        # No similar al correo electrónico
        if email:
            correo_sin_dominio = email.split("@")[0]
            if correo_sin_dominio.lower() in password.lower():
                raise forms.ValidationError(
                    "La contraseña no puede ser similar al correo electrónico."
                )

        # Debe contener letras y números
        if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
            raise forms.ValidationError(
                "La contraseña debe contener letras y números."
            )

        # Debe incluir mayúsculas y minúsculas
        if not re.search(r"[a-z]", password) or not re.search(r"[A-Z]", password):
            raise forms.ValidationError(
                "Debe incluir al menos una letra minúscula y una mayúscula."
            )

        # Lista ampliada de contraseñas comunes
        contrasenas_comunes = {
            "123456", "12345678", "123456789", "password", "contraseña",
            "qwerty", "abc123", "test123", "hola123", "1234abcd",
            "11111111", "iloveyou", "admin", "root", "usuario",
            "qwertyui", "asdfasdf", "clave123"
        }
        if password.lower() in contrasenas_comunes:
            raise forms.ValidationError(
                "La contraseña es demasiado común. Elige una más segura."
            )

        # No solo números
        if password.isdigit():
            raise forms.ValidationError(
                "La contraseña no puede ser completamente numérica."
            )

        # No espacios
        if " " in password:
            raise forms.ValidationError(
                "La contraseña no puede contener espacios."
            )

        # Detectar patrones repetitivos (aaaaaa, 111111, etc.)
        if re.fullmatch(r"(.)\1{5,}", password):
            raise forms.ValidationError(
                "La contraseña no puede repetir el mismo carácter demasiadas veces."
            )

        # Detectar patrones incrementales (abcde, 12345, etc.)
        secuencias_peligrosas = [
            "abcdefghijklmnopqrstuvwxyz",
            "0123456789"
        ]
        for seq in secuencias_peligrosas:
            if password.lower() in seq:
                raise forms.ValidationError(
                    "La contraseña no puede ser una secuencia simple."
                )

        return password
    
    def clean(self):
        """
        Sobrescribimos clean() para comparar ambas contraseñas con mensajes personalizados.
        """
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if not password2:
            self.add_error("password2", "Debes repetir la contraseña.")
            return cleaned_data

        # Si password1 falló anteriormente, evitamos comparar
        if not password1:
            return cleaned_data

        # Verificamos coincidencia
        if password1 != password2:
            self.add_error("password2", "Las contraseñas no coinciden.")

        return cleaned_data