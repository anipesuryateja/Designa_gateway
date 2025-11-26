# Use a slim official Python image
FROM python:3.11-slim

# Set non-interactive build args
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Install system deps needed by some Python packages (lxml/cryptography etc.)
# Keep packages minimal; adjust if you need other system libs.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifest first (cache leveraged by Docker)
COPY requirements.txt .

# Upgrade pip and install requirements
RUN python -m pip install --upgrade pip setuptools wheel \
 && python -m pip install -r requirements.txt

# Copy app source
COPY ./app ./app
# Copy other files if needed (e.g., .env only for local testing; use Azure App Settings for secrets)
# COPY .env .

# Create non-root user and give ownership
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (App Service expects your app to listen on the port it provides, typically 8000 inside container)
EXPOSE 8000

# Use gunicorn with uvicorn workers for production.
# We bind to 0.0.0.0:8000 (App Service container port)
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "600"]
