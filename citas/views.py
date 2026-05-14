from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from datetime import date, datetime, timedelta
from collections import defaultdict
import json

from .models import Cita, Profesional
from usuarios.models import Cliente, Profesional
from usuarios.forms import RegistroProfesionalForm


# ─── DASHBOARD DEL CLIENTE ────────────────────────────────────────────────────
@login_required
def dashboard_cliente(request):
    try:
        perfil_cliente = Cliente.objects.get(email=request.user.email)
    except Cliente.DoesNotExist:
        return render(request, 'error.html', {'mensaje': 'Perfil no encontrado'})

    todas_citas = Cita.objects.filter(cliente=perfil_cliente).order_by('fecha', 'hora')

    # KAN-45: Filtro por fecha
    fecha_filtro = request.GET.get('fecha', '')
    if fecha_filtro:
        try:
            fecha_obj = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
            todas_citas = todas_citas.filter(fecha=fecha_obj)
        except ValueError:
            fecha_filtro = ''

    # KAN-59: Alertas citas próximas (48h)
    hoy = date.today()
    en_dos_dias = hoy + timedelta(days=2)
    citas_proximas = Cita.objects.filter(
        cliente=perfil_cliente,
        fecha__range=[hoy, en_dos_dias],
        estado__in=['PEN', 'CON']
    ).order_by('fecha', 'hora')

    context = {
        'citas': todas_citas,
        'num_pendientes': Cita.objects.filter(cliente=perfil_cliente, estado='PEN').count(),
        'num_aprobadas': Cita.objects.filter(cliente=perfil_cliente, estado='CON').count(),
        'profesionales': Profesional.objects.all(),
        'fecha_filtro': fecha_filtro,
        'citas_proximas': citas_proximas,
        'total_citas': Cita.objects.filter(cliente=perfil_cliente).count(),
    }
    return render(request, 'dashboards/cliente.html', context)


# ─── AGENDAR CITA ─────────────────────────────────────────────────────────────
@login_required
def agendar_cita(request):
    perfil_cliente = get_object_or_404(Cliente, email=request.user.email)

    if request.method == 'POST':
        profesional_id = request.POST.get('profesional')
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')

        try:
            hora_obj = datetime.strptime(hora_str, '%H:%M').time()
            if hora_obj.minute not in [0, 30]:
                messages.error(request, "Las citas deben ser en intervalos de 30 minutos.")
                return redirect('agendar_cita')

            existe = Cita.objects.filter(
                profesional_id=profesional_id,
                fecha=fecha_str,
                hora=hora_str,
                estado__in=['PEN', 'CON']
            ).exists()

            if existe:
                messages.error(request, "El profesional ya tiene una cita en ese horario.")
                return redirect('agendar_cita')

            Cita.objects.create(
                cliente=perfil_cliente,
                profesional_id=profesional_id,
                fecha=fecha_str,
                hora=hora_str,
                estado='PEN'
            )
            messages.success(request, "Cita solicitada exitosamente.")
            return redirect('dashboard_cliente')

        except ValueError:
            messages.error(request, "Error en los datos enviados. Verifica la fecha y hora.")
            return redirect('agendar_cita')

    context = {'profesionales': Profesional.objects.all()}
    return render(request, 'citas/agendar.html', context)


# ─── DASHBOARD DEL PROFESIONAL ────────────────────────────────────────────────
@login_required
def dashboard_profesional(request):
    profesional = get_object_or_404(Profesional, user=request.user)
    todas_citas = Cita.objects.filter(profesional=profesional).order_by('fecha', 'hora')
    hoy = date.today()

    # KAN-51: citas agrupadas por día para el calendario
    citas_por_dia = defaultdict(list)
    for cita in todas_citas:
        citas_por_dia[cita.fecha.isoformat()].append({
            'id': cita.id,
            'hora': cita.hora.strftime('%H:%M'),
            'paciente': cita.cliente.nombre,
            'estado': cita.estado,
        })

    # KAN-52: horas ocupadas por día
    horas_ocupadas_por_dia = defaultdict(list)
    for cita in todas_citas.filter(estado__in=['PEN', 'CON']):
        horas_ocupadas_por_dia[cita.fecha.isoformat()].append(cita.hora.strftime('%H:%M'))

    # KAN-57: citas de hoy
    citas_hoy = todas_citas.filter(fecha=hoy)

    # KAN-50: días del mes para el calendario
    primer_dia_mes = hoy.replace(day=1)
    if hoy.month == 12:
        ultimo_dia_mes = hoy.replace(year=hoy.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        ultimo_dia_mes = hoy.replace(month=hoy.month + 1, day=1) - timedelta(days=1)

    dias_calendario = []
    dia_actual = primer_dia_mes
    while dia_actual <= ultimo_dia_mes:
        iso = dia_actual.isoformat()
        dias_calendario.append({
            'fecha': dia_actual,
            'iso': iso,
            'num_citas': len(citas_por_dia.get(iso, [])),
            'es_hoy': dia_actual == hoy,
            'pasado': dia_actual < hoy,
        })
        dia_actual += timedelta(days=1)

    context = {
        'citas': todas_citas,
        'citas_hoy': citas_hoy,
        'citas_hoy_count': citas_hoy.count(),
        'profesional': profesional,
        'dias_calendario': dias_calendario,
        'citas_por_dia_json': json.dumps(dict(citas_por_dia)),
        'horas_ocupadas_json': json.dumps(dict(horas_ocupadas_por_dia)),
        'mes_nombre': hoy.strftime('%B %Y'),
        'hoy_iso': hoy.isoformat(),
        'total_pendientes': todas_citas.filter(estado='PEN').count(),
        'total_confirmadas': todas_citas.filter(estado='CON').count(),
    }
    return render(request, 'dashboards/profesional.html', context)


# ─── DASHBOARD ADMIN ──────────────────────────────────────────────────────────
@staff_member_required
def dashboard_admin(request):
    context = {
        'total_usuarios': User.objects.count(),
        'total_clientes': Cliente.objects.count(),
        'total_profesionales': Profesional.objects.count(),
        'total_citas': Cita.objects.count(),
        'profesionales_lista': Profesional.objects.all(),
        # ESTA ES LA LÍNEA CLAVE:
        'clientes_lista': Cliente.objects.all().order_by('nombre'), 
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


# ─── CAMBIAR ESTADO ───────────────────────────────────────────────────────────
def cambiar_estado_cita(request, cita_id, nuevo_estado):
    cita = get_object_or_404(Cita, id=cita_id)
    estados_validos = ['PEN', 'CON', 'CAN', 'FIN']
    if nuevo_estado in estados_validos:
        if request.user.is_staff or cita.profesional.user == request.user:
            cita.estado = nuevo_estado
            cita.save()
    return redirect('dashboard_profesional')


# ─── ELIMINAR CITA ────────────────────────────────────────────────────────────
def eliminar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    cita.delete()
    return redirect('dashboard_cliente')


# ─── API HORAS OCUPADAS ───────────────────────────────────────────────────────
def obtener_horas_ocupadas(request):
    profesional_id = request.GET.get('profesional_id')
    fecha = request.GET.get('fecha')
    citas_ocupadas = Cita.objects.filter(
        profesional_id=profesional_id,
        fecha=fecha,
        estado__in=['PEN', 'CON']
    ).values_list('hora', flat=True)
    horas_lista = [hora.strftime('%H:%M') for hora in citas_ocupadas]
    return JsonResponse({'horas_ocupadas': horas_lista})


# ─── API CITAS POR FECHA (AJAX calendario) ────────────────────────────────────
@login_required
def citas_por_fecha(request):
    profesional = get_object_or_404(Profesional, user=request.user)
    fecha_str = request.GET.get('fecha', date.today().isoformat())
    try:
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Fecha inválida'}, status=400)

    citas = Cita.objects.filter(profesional=profesional, fecha=fecha_obj).order_by('hora')
    data = [{
        'id': c.id,
        'hora': c.hora.strftime('%H:%M'),
        'paciente': c.cliente.nombre,
        'estado': c.estado,
        'estado_display': c.get_estado_display(),
    } for c in citas]
    return JsonResponse({'citas': data, 'fecha': fecha_str})
# ─── AGENDAR CITA DESDE PROFESIONAL ──────────────────────────────────────────
@login_required
def agendar_cita_profesional(request):
    profesional = get_object_or_404(Profesional, user=request.user)
    clientes = Cliente.objects.all().order_by('nombre')

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')

        try:
            hora_obj = datetime.strptime(hora_str, '%H:%M').time()
            if hora_obj.minute not in [0, 30]:
                messages.error(request, "Las citas deben ser en intervalos de 30 minutos.")
                return redirect('agendar_cita_profesional')

            existe = Cita.objects.filter(
                profesional=profesional,
                fecha=fecha_str,
                hora=hora_str,
                estado__in=['PEN', 'CON']
            ).exists()

            if existe:
                messages.error(request, "Ya tienes una cita en ese horario.")
                return redirect('agendar_cita_profesional')

            Cita.objects.create(
                cliente_id=cliente_id,
                profesional=profesional,
                fecha=fecha_str,
                hora=hora_str,
                estado='CON'
            )
            messages.success(request, "Cita agendada exitosamente.")
            return redirect('dashboard_profesional')

        except ValueError:
            messages.error(request, "Error en los datos. Verifica fecha y hora.")
            return redirect('agendar_cita_profesional')

    # ← Aquí van las horas, antes del context
    horas = []
    for h in range(8, 18):
        horas.append(f"{str(h).zfill(2)}:00")
        horas.append(f"{str(h).zfill(2)}:30")

    context = {
        'profesional': profesional,
        'clientes': clientes,
        'horas': horas,
    }
    return render(request, 'citas/agendar_profesional.html', context)


# ─── GESTIÓN DE CLIENTES (ADMIN) ──────────────────────────────────────────────
@staff_member_required
def listar_clientes(request):
    clientes = Cliente.objects.all().order_by('nombre')
    return render(request, 'dashboards/admin_clientes.html', {'clientes': clientes})


# ─── GESTIÓN DE PROFESIONALES (ADMIN) ─────────────────────────────────────────
@staff_member_required
def editar_profesional(request, profesional_id):
    profesional = get_object_or_404(Profesional, id=profesional_id)
    if request.method == 'POST':
        form = RegistroProfesionalForm(request.POST, instance=profesional)
        if form.is_valid():
            form.save()
            messages.success(request, "Profesional actualizado.")
            return redirect('dashboard_admin')
    else:
        form = RegistroProfesionalForm(instance=profesional)
    return render(request, 'dashboards/admin_crear_profesional.html', {'form': form, 'editando': True})

@staff_member_required
def eliminar_profesional(request, profesional_id):
    profesional = get_object_or_404(Profesional, id=profesional_id)
    # Eliminamos el usuario asociado para no dejar basura en la base de datos
    if profesional.user:
        profesional.user.delete()
    profesional.delete()
    messages.success(request, "Profesional eliminado correctamente.")
    return redirect('dashboard_admin')

@staff_member_required
def eliminar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    # Buscamos el usuario por email para borrar su acceso también
    User.objects.filter(email=cliente.email).delete()
    cliente.delete()
    messages.success(request, "Paciente eliminado correctamente.")
    return redirect('dashboard_admin')