#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser if it doesn't exist
python manage.py shell << END
from django.contrib.auth import get_user_model
import os
User = get_user_model()
if not User.objects.filter(username=os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')).exists():
    User.objects.create_superuser(
        os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'),
        os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com'),
        os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
    )
END 