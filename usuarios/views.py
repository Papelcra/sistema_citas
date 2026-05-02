from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RegistroClienteForm
from django.contrib.auth.decorators import login_required
from .models import Profesional, Cliente
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from .forms import RegistroProfesionalForm

def home_redirect(request):
    if not request.user.is_authenticated:
        return render(request, 'public_index.html')
    
    # 1. ¿Es el Administrador de la empresa? (Tiene el check de Staff)
    if request.user.is_staff:
        return redirect('dashboard_admin') # El panel con los 3 cuadros y la tabla
    
    # 2. ¿Es un Profesional? (Buscamos si existe en la tabla Profesional)
    if Profesional.objects.filter(user=request.user).exists():
        return redirect('dashboard_profesional')
    
    # 3. Si no es ninguno de los anteriores, es un Cliente
    return redirect('dashboard_cliente')

class RegistroClienteView(CreateView):
    template_name = 'registro.html'
    form_class = RegistroClienteForm
    success_url = reverse_lazy('login')


@method_decorator(staff_member_required, name='dispatch')
class CrearProfesionalView(CreateView):
    model = Profesional
    form_class = RegistroProfesionalForm
    template_name = 'dashboards/admin_crear_profesional.html'
    success_url = '/panel/admin/' # Regresa al dashboard tras crear al doctor