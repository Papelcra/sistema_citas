import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings') # Ajusta 'config'
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Configura estas variables en el panel de Render o déjalas fijas aquí para pruebas
username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin12345')

if not User.objects.filter(username=username).exists():
    print(f"Creando superusuario: {username}...")
    User.objects.create_superuser(username, email, password)
    print("Superusuario creado con éxito.")
else:
    print("El superusuario ya existe.")