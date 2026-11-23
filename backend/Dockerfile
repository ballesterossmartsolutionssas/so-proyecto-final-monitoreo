# Imagen del backend: Python 3.12 en Debian slim (pequeña y con glibc).
FROM python:3.12-slim

# No generar .pyc y ver los logs al instante en `docker logs`.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Primero solo las dependencias: Docker reutiliza esta capa mientras
# requirements.txt no cambie, y las reconstrucciones son rápidas.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Ejecutar sin privilegios de root.
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 5000

# Docker marca el contenedor como "healthy" solo si /health responde.
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=2)"

# 1 proceso con 8 hilos: así cada réplica tiene UN solo juego de contadores
# de Prometheus (con varios procesos cada uno tendría los suyos y las cifras saltarían).
CMD ["gunicorn", "-w", "1", "--threads", "8", "-b", "0.0.0.0:5000", "--access-logfile", "-", "app:app"]
