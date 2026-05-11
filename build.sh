#!/usr/bin/env bash
# Salir si hay errores
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Recolectar archivos estáticos
python manage.py collectstatic --no-input

# Aplicar migraciones de la base de datos
python manage.py migrate

# CREAR EL SUPERUSUARIO AUTOMÁTICAMENTE
python create_admin.py