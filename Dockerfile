# Use a lightweight official Python image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Enable filesystem storage inside Docker environment
ENV MLFLOW_ALLOW_FILE_STORE=true

# Install dependencies first (leverages Docker caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files and MLflow tracking data
COPY app.py .
COPY mlruns/ ./mlruns/

# Expose FastAPI default port
EXPOSE 8000

# Start Uvicorn server bound to all interfaces
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
