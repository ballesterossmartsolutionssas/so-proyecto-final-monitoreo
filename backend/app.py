"""Backend del proyecto final de Sistemas Operativos.

API mínima en Flask. Cada réplica se identifica con INSTANCE_ID y expone
/metrics en formato Prometheus (contador de solicitudes, histograma de
latencia y solicitudes en curso).
"""
import hashlib
import os
import socket
import time
from datetime import datetime, timezone

from flask import Flask, Response, g, jsonify, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)

INSTANCE_ID = os.getenv("INSTANCE_ID", "0")
HOSTNAME = socket.gethostname()

app = Flask(__name__)

# ---------------------------------------------------------------- métricas
REQUESTS = Counter(
    "app_requests_total",
    "Solicitudes HTTP atendidas por el backend",
    ["instance_id", "method", "endpoint", "status"],
)
LATENCY = Histogram(
    "app_request_latency_seconds",
    "Tiempo que tarda el backend en responder",
    ["instance_id", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 1.0, 2.5),
)
IN_PROGRESS = Gauge(
    "app_requests_in_progress",
    "Solicitudes que el backend está atendiendo en este momento",
    ["instance_id"],
)
APP_INFO = Info("app_build", "Datos de la réplica del backend")
APP_INFO.info({"instance_id": INSTANCE_ID, "hostname": HOSTNAME, "version": "1.0.0"})

# Rutas que no se miden (las consultan Prometheus y el healthcheck cada pocos segundos)
NO_MEDIR = {"/metrics", "/health"}


@app.before_request
def _inicio():
    g.t0 = time.perf_counter()
    if request.path not in NO_MEDIR:
        IN_PROGRESS.labels(INSTANCE_ID).inc()


@app.after_request
def _fin(resp):
    resp.headers["X-Instance-Id"] = INSTANCE_ID
    if request.path not in NO_MEDIR:
        endpoint = request.url_rule.rule if request.url_rule else "desconocido"
        LATENCY.labels(INSTANCE_ID, endpoint).observe(time.perf_counter() - g.t0)
        REQUESTS.labels(INSTANCE_ID, request.method, endpoint, str(resp.status_code)).inc()
        IN_PROGRESS.labels(INSTANCE_ID).dec()
    return resp


# ---------------------------------------------------------------- rutas
@app.get("/")
def inicio():
    return jsonify(
        mensaje=f"Hola desde el backend {INSTANCE_ID}",
        instancia=INSTANCE_ID,
        contenedor=HOSTNAME,
        hora_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )


@app.get("/api/trabajo")
def trabajo():
    """Simula una operación que consume CPU durante unos milisegundos (?ms=, máximo 500)."""
    ms = min(max(request.args.get("ms", default=50, type=int), 1), 500)
    fin = time.perf_counter() + ms / 1000
    vueltas = 0
    dato = INSTANCE_ID.encode()
    while time.perf_counter() < fin:
        dato = hashlib.sha256(dato).digest()
        vueltas += 1
    return jsonify(instancia=INSTANCE_ID, ms_solicitados=ms, iteraciones_sha256=vueltas)


@app.get("/health")
def health():
    return jsonify(estado="ok", instancia=INSTANCE_ID)


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
