FROM python:3.11-slim

WORKDIR /app

# Copiar requerimientos y el archivo con doble 's' como está en tu captura
COPY requirementss.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Cloud Run requiere escuchar en 0.0.0.0 y usar el puerto de la variable $PORT
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}