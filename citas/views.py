from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import Cita, Profesional, Cliente
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import AgendarCitaForm
from usuarios.models import Cliente
from usuarios.forms import RegistroProfesionalForm
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import date

# DASHBOARD DEL CLIENTE
@login_required
def dashboard_cliente(request):
    # Traemos las citas donde el email del cliente coincida con el del usuario logueado
    citas = Cita.objects.filter(cliente__email=request.user.email).order_by('-fecha')
    return render(request, 'dashboards/cliente.html', {'citas': citas})

# DASHBOARD DEL PROFESIONAL
@login_required
def dashboard_profesional(request):
    profesional = get_object_or_404(Profesional, user=request.user)
    citas = Cita.objects.filter(profesional=profesional).order_by('fecha', 'hora')
    
    # Contar solo las que son para la fecha actual
    citas_hoy_count = citas.filter(fecha=date.today()).count()
    
    return render(request, 'dashboards/profesional.html', {
        'citas': citas,
        'citas_hoy_count': citas_hoy_count,
        'profesional': profesional
    })

@staff_member_required
def dashboard_admin(request):
    context = {
        'total_usuarios': User.objects.count(),
        'total_clientes': Cliente.objects.count(),
        'total_profesionales': Profesional.objects.count(),
        'total_citas': Cita.objects.count(),
        'profesionales_lista': Profesional.objects.all(), # Para la tabla
    }
    return render(request, 'dashboards/admin_dashboard.html', context)

@staff_member_required
def crear_profesional(request):
    if request.method == 'POST':
        form = RegistroProfesionalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard_admin')
    else:
        form = RegistroProfesionalForm()
    
    return render(request, 'dashboards/admin_crear_profesional.html', {'form': form})
@login_required
def agendar_cita(request):
    if request.method == 'POST':
        form = AgendarCitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            # Buscamos al cliente asociado al correo del usuario logueado
            try:
                cliente = Cliente.objects.get(email=request.user.email)
                cita.cliente = cliente
                cita.save()
                return redirect('dashboard_cliente')
            except Cliente.DoesNotExist:
                # Si por alguna razón no hay cliente, mostramos error
                return render(request, 'citas/agendar.html', {'form': form, 'error': 'Perfil de cliente no encontrado'})
    else:
        form = AgendarCitaForm()
    
    return render(request, 'citas/agendar.html', {'form': form})


from django.views.decorators.http import require_POST

@require_POST
@login_required
def cambiar_estado_cita(request, cita_id, nuevo_estado):
    cita = get_object_or_404(Cita, id=cita_id)

    estados_validos = ['PEN', 'CON', 'CAN', 'FIN']

    if nuevo_estado in estados_validos:
        if request.user.is_staff or cita.profesional.user == request.user:
            cita.estado = nuevo_estado
            cita.save()

    return redirect('dashboard_profesional')

def eliminar_cita(request, cita_id):
    # Buscamos la cita directamente por su ID
    cita = get_object_or_404(Cita, id=cita_id)
    
    # La borramos
    cita.delete()
    
    # Redirigimos al dashboard del cliente
    return redirect('dashboard_cliente')