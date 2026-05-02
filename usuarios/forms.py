from django import forms
from django.contrib.auth.models import User
from .models import Cliente, Profesional
from django.db import transaction

class RegistroClienteForm(forms.ModelForm):
    # Campos personalizados con etiquetas en español y clases de Bootstrap
    username = forms.CharField(
        label="Nombre de Usuario",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: julian123'})
    )
    first_name = forms.CharField(
        label="Nombres",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'})
    )
    last_name = forms.CharField(
        label="Apellidos",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tus apellidos'})
    )
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'})
    )
    telefono = forms.CharField(
        label="Teléfono de Contacto",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 3001234567'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Crea una clave segura'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email

    def save(self, commit=True):
        # Usamos transaction.atomic para asegurar que se creen ambos o ninguno
        with transaction.atomic():
            user = super().save(commit=False)
            user.set_password(self.cleaned_data["password"])
            user.save() # Guarda en la tabla auth_user (indispensable para login)
            
            # Crea el perfil de Cliente vinculado a ese usuario
            Cliente.objects.create(
                nombre=f"{user.first_name} {user.last_name}",
                email=user.email,
                telefono=self.cleaned_data['telefono']
            )
        return user
    
class RegistroProfesionalForm(forms.ModelForm):
    username = forms.CharField(label="Usuario", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Profesional
        fields = ['nombre', 'especialidad'] # Solo los datos del doctor
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'especialidad': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        with transaction.atomic():
            # 1. Crea el User para que el médico pueda hacer login
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password'],
                first_name=self.cleaned_data['nombre']
            )
            # 2. Crea el perfil Profesional vinculado
            profesional = super().save(commit=False)
            profesional.user = user
            if commit:
                profesional.save()
        return profesional