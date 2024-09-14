#!/bin/sh

set -e

# Wait for the database to be ready
until nc -z db 5432; do
  echo "Waiting for PostgreSQL..."
  sleep 1
done
echo "PostgreSQL is up and running."

# Run migrations
echo "Running migrations..."
pipenv run python manage.py migrate

# Create superuser if it doesn't exist
if [ "$CREATE_SUPERUSER" = "true" ]; then
  echo "Creating superuser..."

  pipenv run python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
username = 'admin';
password = 'Admin123@';
email = 'admin@example.com';
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print('Superuser created.')
else:
    print('Superuser already exists.')
"
fi

# Start the Django server
echo "Starting Django server..."
exec pipenv run python manage.py runserver 0.0.0.0:8000
