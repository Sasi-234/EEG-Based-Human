# Dockerfile for EEG Emotion Recognition System
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libhdf5-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY backend/ /app/backend/
COPY manage.py /app/

# Create necessary directories
RUN mkdir -p /app/media /app/static /app/logs /app/trained_models

# Collect static files
WORKDIR /app/backend
RUN python ../manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "python ../manage.py migrate && python ../manage.py runserver 0.0.0.0:8000"]

# Made with Bob
