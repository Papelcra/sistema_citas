from django.db import models
from django.contrib.auth.models import User

class Profesional(models.Model):
    # Esto vincula al Profesional con la cuenta de inicio de sesión
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)
    # ... otros campos que ya tengas ...

    def __str__(self):
        return f"Dr. {self.nombre} - {self.especialidad}"

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15)

    def __str__(self):
        return self.nombre