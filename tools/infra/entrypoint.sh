#!/bin/bash

# Migrate DB
python3 manage.py migrate --noinput

# Collect static files
python3 manage.py collectstatic --noinput

# Compile language translations
python3 manage.py compilemessages

# Create superuser (optional - usually not done in production automatically)
python3 manage.py superuser --username superadmin --email superadmin@example.com --password userpassword

# Run server
gunicorn --config gunicorn.conf.py config.wsgi:application
