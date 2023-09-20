web: gunicorn --bind 127.0.0.1:8000 --workers=1 --threads=15 config.wsgi:application
# Uncomment the following lines to run celery
# celery_beat: celery -A config beat --scheduler django_celery_beat.schedulers:DatabaseScheduler -l INFO
# celery_worker: celery -A config worker -n worker -l INFO
