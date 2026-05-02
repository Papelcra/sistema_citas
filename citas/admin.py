from django.contrib import admin
from .models import Cita

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    # Esto hará que la lista de citas sea muy legible
    list_display = ('fecha', 'hora', 'cliente', 'profesional', 'estado')
    
    # Filtros laterales para que el admin encuentre rápido
    list_filter = ('estado', 'fecha', 'profesional')
    
    # Buscador por nombre de cliente o profesional
    search_fields = ('cliente__nombre', 'profesional__nombre')
    
    # Permitir cambiar el estado directamente desde la lista
    list_editable = ('estado',)