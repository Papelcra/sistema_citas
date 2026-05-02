from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from usuarios.views import home_redirect  # <--- Cambio aquí
from citas.views import agendar_cita, dashboard_cliente, dashboard_profesional, dashboard_admin, cambiar_estado_cita, eliminar_cita  # <--- Asegúrate de importar todas las funciones necesarias
from usuarios.views import RegistroClienteView, CrearProfesionalView
from citas import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('dashboard/', dashboard_cliente, name='dashboard_cliente'),
    path('registro/', RegistroClienteView.as_view(), name='registro'),
    path('dashboard/agendar/', agendar_cita, name='agendar_cita'),
    path('dashboard/profesional/', dashboard_profesional, name='dashboard_profesional'), # Nueva
    path('panel/admin/', dashboard_admin, name='dashboard_admin'),
    path('panel/admin/crear-profesional/', CrearProfesionalView.as_view(), name='crear_profesional'),
    path('cita/estado/<int:cita_id>/<str:nuevo_estado>/', cambiar_estado_cita, name='cambiar_estado_cita'),
    path('cita/eliminar/<int:cita_id>/', eliminar_cita, name='eliminar_cita'),


]   