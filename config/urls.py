from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from usuarios.views import home_redirect
from citas.views import (
    agendar_cita, agendar_cita_profesional, dashboard_cliente, 
    dashboard_profesional, dashboard_admin, cambiar_estado_cita, 
    eliminar_cita, obtener_horas_ocupadas, citas_por_fecha,
    editar_profesional, eliminar_profesional, eliminar_cliente
)
from usuarios.views import RegistroClienteView, CrearProfesionalView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # Dashboards
    path('dashboard/', dashboard_cliente, name='dashboard_cliente'),
    path('dashboard/profesional/', dashboard_profesional, name='dashboard_profesional'),
    path('panel/admin/', dashboard_admin, name='dashboard_admin'),

    # Citas
    path('dashboard/agendar/', agendar_cita, name='agendar_cita'),
    path('dashboard/profesional/agendar/', agendar_cita_profesional, name='agendar_cita_profesional'),
    path('cita/estado/<int:cita_id>/<str:nuevo_estado>/', cambiar_estado_cita, name='cambiar_estado_cita'),
    path('cita/eliminar/<int:cita_id>/', eliminar_cita, name='eliminar_cita'),
    
    # Gestión Admin (CRUD)
    path('panel/admin/crear-profesional/', CrearProfesionalView.as_view(), name='crear_profesional'),
    path('panel/admin/editar-profesional/<int:profesional_id>/', editar_profesional, name='editar_profesional'),
    path('panel/admin/eliminar-profesional/<int:profesional_id>/', eliminar_profesional, name='eliminar_profesional'),
    path('panel/admin/eliminar-cliente/<int:cliente_id>/', eliminar_cliente, name='eliminar_cliente'),

    # Registro y APIs
    path('registro/', RegistroClienteView.as_view(), name='registro'),
    path('api/horas-ocupadas/', obtener_horas_ocupadas, name='obtener_horas_ocupadas'),
    path('api/citas-por-fecha/', citas_por_fecha, name='citas_por_fecha'),
]