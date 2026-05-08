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
from django.core.exceptions import ValidationError
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cita, Profesional, Cliente # Asegúrate de importar Cliente
from datetime import datetime

# DASHBOARD DEL CLIENTE
@login_required
def dashboard_cliente(request):
    try:
        # Buscamos por email para evitar el FieldError que viste antes
        perfil_cliente = Cliente.objects.get(email=request.user.email) 
    except Cliente.DoesNotExist:
        return render(request, 'error.html', {'mensaje': 'Perfil no encontrado'})

    todas_citas = Cita.objects.filter(cliente=perfil_cliente).order_by('fecha', 'hora') #
    
    context = {
        'citas': todas_citas,
        # Filtramos por los códigos de tu models.py: 'PEN' y 'CON'
        'num_pendientes': todas_citas.filter(estado='PEN').count(), 
        'num_aprobadas': todas_citas.filter(estado='CON').count(),
        'profesionales': Profesional.objects.all(),
    }
    return render(request, 'dashboards/cliente.html', context)

@login_required
def agendar_cita(request):
    # Obtener el perfil del cliente
    perfil_cliente = get_object_or_404(Cliente, email=request.user.email)

    if request.method == 'POST':
        profesional_id = request.POST.get('profesional')
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')
        
        # Lógica de validación de horarios y solapamiento...
        # (Aquí va el código que ya tienes para guardar la cita)
        
        Cita.objects.create(
            cliente=perfil_cliente, 
            profesional_id=profesional_id,
            fecha=fecha_str,
            hora=hora_str,
            estado='PEN'
        )
        messages.success(request, "Cita solicitada exitosamente.")
        return redirect('dashboard_cliente') # Redirige al dashboard tras agendar
    
    # IMPORTANTE: Aquí enviamos al archivo que mencionaste
    context = {
        'profesionales': Profesional.objects.all(),
    }
    return render(request, 'citas/agendar.html', context)


# DASHBOARD DEL PROFESIONAL
@login_required
def dashboard_profesional(request):
    profesional = get_object_or_404(Profesional, user=request.user)
    # Ordenar por fecha y hora para que vea su agenda en orden
    citas = Cita.objects.filter(profesional=profesional).order_by('fecha', 'hora')
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

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Cita, Profesional
from datetime import datetime



@login_required
def agendar_cita(request):
    # 1. Obtener la instancia de Cliente usando el email (evita FieldError)
    # Buscamos el perfil del cliente vinculado al usuario que está navegando
    perfil_cliente = get_object_or_404(Cliente, email=request.user.email)

    if request.method == 'POST':
        profesional_id = request.POST.get('profesional')
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')
        
        try:
            # Validar formato de hora (solo :00 o :30)
            hora_obj = datetime.strptime(hora_str, '%H:%M').time()
            if hora_obj.minute not in [0, 30]:
                messages.error(request, "Las citas deben ser en intervalos de 30 minutos.")
                return redirect('agendar_cita')

            # Validar solapamiento (Requerimiento Funcional 4)
            # Verificamos si el profesional ya tiene una cita PEN (Pendiente) o CON (Confirmada)
            existe = Cita.objects.filter(
                profesional_id=profesional_id,
                fecha=fecha_str,
                hora=hora_str,
                estado__in=['PEN', 'CON']
            ).exists()

            if existe:
                messages.error(request, "El profesional ya tiene una cita en ese horario.")
                return redirect('agendar_cita')

            # 2. Guardar la cita en la base de datos
            Cita.objects.create(
                cliente=perfil_cliente, 
                profesional_id=profesional_id,
                fecha=fecha_str,
                hora=hora_str,
                estado='PEN' # Se crea como Pendiente por defecto
            )
            
            messages.success(request, "Cita solicitada exitosamente.")
            # Después de guardar, regresamos al Dashboard para ver la lista actualizada
            return redirect('dashboard_cliente')

        except ValueError:
            messages.error(request, "Error en los datos enviados. Por favor verifica la fecha y hora.")
            return redirect('agendar_cita')
    
    # 3. Respuesta para peticiones GET (cuando el usuario entra a la página)
    context = {
        'profesionales': Profesional.objects.all(),
        # No incluimos 'citas' aquí porque esta vista solo debe mostrar el formulario
    }
    
    # IMPORTANTE: Esta es la ruta a tu archivo en templates/citas/agendar.html
    return render(request, 'citas/agendar.html', context)



def cambiar_estado_cita(request, cita_id, nuevo_estado):
    cita = get_object_or_404(Cita, id=cita_id)
    
    # Mapeo de seguridad para asegurar que solo entren códigos válidos
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


def validar_horario(hora):
    # La cita dura 30 minutos, por lo que solo permitimos minutos 00 o 30 
    if hora.minute not in [0, 30]:
        raise ValidationError("Las citas solo pueden agendarse en intervalos de 30 minutos (ej: 10:00 o 10:30).")

    # También puedes limitar el rango de atención (ej: 8 AM a 6 PM)
    if hora.hour < 8 or hora.hour >= 18:
        raise ValidationError("El horario de atención es de 08:00 AM a 06:00 PM.")
    

from django.http import JsonResponse
from .models import Cita # Ajusta según el nombre de tu modelo

def obtener_horas_ocupadas(request):
    profesional_id = request.GET.get('profesional_id')
    fecha = request.GET.get('fecha')
    
    # Filtramos las citas para ese profesional en esa fecha
    citas_ocupadas = Cita.objects.filter(
        profesional_id=profesional_id, 
        fecha=fecha
    ).values_list('hora', flat=True)
    
    # Convertimos las horas a formato string para JS (ej: "10:00:00")
    horas_lista = [hora.strftime('%H:%M') for hora in citas_ocupadas]
    
    return JsonResponse({'horas_ocupadas': horas_lista})