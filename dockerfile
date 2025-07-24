FROM python:3.11

WORKDIR /app

# Install netcat for the entrypoint script to wait for the database
RUN apt-get update && apt-get install -y --no-install-recommends netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

EXPOSE 8000

# This MUST be 0.0.0.0:8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]