from django import forms
from .models import Cita
from usuarios.models import Profesional
from django.utils import timezone
from datetime import time

class AgendarCitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['profesional', 'fecha', 'hora', 'notas']
        widgets = {
            'profesional': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Opcional: motivo de la consulta'}),
        }
        labels = {
            'profesional': 'Seleccione al Profesional',
            'fecha': 'Fecha de la Cita',
            'hora': 'Hora de la Cita',
            'notas': 'Notas Adicionales',
        }

    def clean(self):
        cleaned_data = super().clean()
        profesional = cleaned_data.get('profesional')
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')

        if fecha and hora:
            # 1. Validación: No permitir fechas pasadas
            if fecha < timezone.now().date():
                raise forms.ValidationError("No puedes agendar una cita en una fecha que ya pasó.")
            
            # 2. Validación: Horario de oficina (Ejemplo: 8 AM a 6 PM)
            hora_inicio = time(8, 0)
            hora_fin = time(18, 0)
            if not (hora_inicio <= hora <= hora_fin):
                raise forms.ValidationError("El horario de atención es de 8:00 AM a 6:00 PM.")

        if profesional and fecha and hora:
            # 3. Validación: Solapamiento (ya la tenías, pero asegúrate de excluir la cita actual si es edición)
            existe_cita = Cita.objects.filter(
                profesional=profesional,
                fecha=fecha,
                hora=hora
            ).exclude(estado='CAN')
            
            if self.instance.pk: # Si estamos editando, excluimos la cita actual
                existe_cita = existe_cita.exclude(pk=self.instance.pk)

            if existe_cita.exists():
                raise forms.ValidationError(
                    f"Lo sentimos, el profesional {profesional.nombre} ya tiene una cita a esa hora."
                )
        return cleaned_data