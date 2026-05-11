#!/usr/bin/env bash
# Salir si hay errores
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Recolectar estáticos
python manage.py collectstatic --no-input

# ESTA ES LA LÍNEA CLAVE: Crear las tablas en Render
python manage.py migrate

# Crear el superusuario (el script que hicimos antes)
python create_admin.py