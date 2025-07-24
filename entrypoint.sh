#!/bin/sh

# Wait for the database to be ready
echo "Waiting for postgres..."

# The 'db' name comes from your docker-compose.yml service name
while ! nc -z db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

# Run database migrations
python manage.py migrate

# Execute the command passed to the entrypoint (the CMD from the Dockerfile)
exec "$@"