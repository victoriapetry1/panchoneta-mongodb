#!/bin/bash

# Baja contenedores, elimina volúmenes, imágenes huérfanas
docker compose down -v --remove-orphans --rmi all

# Crear migraciones y aplicarlas
docker compose run --rm manage makemigrations
docker compose run --rm manage migrate

# Levantar solo el backend en modo detached (background)
docker compose up backend -d

# Crear superusuario sin interacción
docker compose run --rm manage createsuperuser --noinput --username admin --email admin@example.com

# Establecer contraseña del superusuario (porque --noinput no la setea)
docker compose run --rm manage shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); u=User.objects.get(username='admin'); u.set_password('admin'); u.save()"

# Cargar datos iniciales (fixtures)
docker compose run --rm manage loaddata initial_data
