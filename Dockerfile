FROM python:3.10-slim
WORKDIR /app
ENV MLFLOW_ALLOW_FILE_STORE=true
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY iris_model/ ./iris_model/
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
