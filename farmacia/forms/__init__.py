from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from farmacia.models import Rol

Usuario = get_user_model()


class LoginForm(forms.Form):
    identificador = forms.CharField(label="Usuario o email", max_length=255,
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': True, 'placeholder': 'usuario o email'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}))
    remember = forms.BooleanField(label="Mantener sesión", required=False)


class TwoFactorForm(forms.Form):
    code = forms.CharField(label="Código de verificación", max_length=6,
                           widget=forms.TextInput(attrs={'class': 'form-control text-center', 'placeholder': '123456', 'inputmode': 'numeric'}))


class RegistroForm(forms.ModelForm):
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Repetir contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    rol = forms.ModelChoiceField(queryset=Rol.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    perfil = forms.ChoiceField(
        label="Tipo de acceso",
        choices=[('normal', 'Usuario normal'), ('staff', 'Staff (acceso panel admin)')],
        initial='normal',
        widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'tipo_documento',
                  'numero_documento', 'telefono', 'rol']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-control'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        if self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise ValidationError("Las contraseñas no coinciden.")
        return self.cleaned_data['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tu@email.com'}))


class PasswordResetConfirmForm(forms.Form):
    password1 = forms.CharField(label="Nueva contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Repetir contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password1') != cleaned.get('password2'):
            raise ValidationError("Las contraseñas no coinciden.")
        return cleaned


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono', 'foto']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }
