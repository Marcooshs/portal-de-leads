#!/usr/bin/env bash
set -e

echo ">> Aplicando migrações..."
until python manage.py migrate --noinput; do
  echo "DB indisponível, tentando novamente em 2s..."
  sleep 2
done

if [ "${COLLECTSTATIC}" = "1" ]; then
  echo ">> Coletando estáticos..."
  python manage.py collectstatic --noinput || true
fi

if [ "${DJANGO_ENV}" = "prod" ]; then
  echo ">> Iniciando Gunicorn (produção)..."
  exec gunicorn app.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60
else
  echo ">> Iniciando runserver (desenvolvimento)..."
  exec python manage.py runserver 0.0.0.0:8000
fi