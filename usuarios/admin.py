from django.contrib import admin
from .models import Profesional, Cliente

@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especialidad')
    search_fields = ('nombre', 'especialidad')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono')
    search_fields = ('nombre', 'email')