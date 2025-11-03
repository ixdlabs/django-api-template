#!/bin/bash

until python manage.py showmigrations | grep '\[X\] 0001_initial'; do
  echo "Migrations not finished, waiting..."
  sleep 2
done

celery -A config worker --loglevel=info
