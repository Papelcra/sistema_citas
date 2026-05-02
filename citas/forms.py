from django import forms
from .models import Cita
from usuarios.models import Profesional

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

        if profesional and fecha and hora:
            # Validación: ¿Tiene este profesional otra cita a esa misma hora y fecha?
            existe_cita = Cita.objects.filter(
                profesional=profesional,
                fecha=fecha,
                hora=hora
            ).exclude(estado='CAN').exists() # Ignoramos las canceladas

            if existe_cita:
                raise forms.ValidationError(
                    f"Lo sentimos, el {profesional.nombre} ya tiene una cita programada para esa fecha y hora."
                )
        return cleaned_data