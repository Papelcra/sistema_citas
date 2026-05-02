from django.db import models
from usuarios.models import Cliente, Profesional

class Cita(models.Model):
    ESTADOS = [
        ('PEN', 'Pendiente'),
        ('CON', 'Confirmada'),
        ('CAN', 'Cancelada'),
        ('FIN', 'Finalizada'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=3, choices=ESTADOS, default='PEN')
    notas = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.fecha} {self.hora} - {self.cliente} con {self.profesional}"