web: cd backend && . venv/bin/activate && python manage.py migrate && gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT

