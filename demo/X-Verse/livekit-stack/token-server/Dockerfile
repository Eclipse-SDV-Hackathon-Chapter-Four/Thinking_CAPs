# Lightweight Python base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure stdout/stderr are unbuffered
ENV PYTHONUNBUFFERED=1

# Application working directory
WORKDIR /app

# Update pip and install runtime dependencies
# aiohttp is used for the HTTP server
# livekit-api is used for JWT token generation
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir aiohttp livekit-api

# Copy application source
COPY app.py .

# Expose token server port
EXPOSE 8080

# Run token server
CMD ["python", "app.py"]
