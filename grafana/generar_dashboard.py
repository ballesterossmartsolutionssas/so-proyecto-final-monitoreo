"""Genera grafana/dashboards/infraestructura.json (uso: python grafana/generar_dashboard.py)."""
import json
from pathlib import Path

DS = {"type": "prometheus", "uid": "prometheus"}
_id = 0


def panel(title, exprs, x, y, w=12, h=8, unit="short", kind="timeseries", desc="", legend=None, stack=False, decimals=None):
    global _id
    _id += 1
    targets = []
    for i, e in enumerate(exprs):
        expr, fmt = e if isinstance(e, tuple) else (e, legend[i] if legend else "")
        targets.append({"datasource": DS, "expr": expr, "legendFormat": fmt, "refId": chr(65 + i)})
    p = {
        "id": _id, "type": kind, "title": title, "description": desc, "datasource": DS,
        "gridPos": {"x": x, "y": y, "w": w, "h": h}, "targets": targets,
        "fieldConfig": {"defaults": {"unit": unit}, "overrides": []},
        "options": {},
    }
    if decimals is not None:
        p["fieldConfig"]["defaults"]["decimals"] = decimals
    if kind == "timeseries":
        p["fieldConfig"]["defaults"]["custom"] = {
            "lineWidth": 2, "fillOpacity": 12, "showPoints": "never",
            "stacking": {"mode": "normal" if stack else "none", "group": "A"},
        }
        p["options"] = {"legend": {"displayMode": "table", "placement": "bottom", "calcs": ["mean", "max", "lastNotNull"]},
                        "tooltip": {"mode": "multi", "sort": "desc"}}
    elif kind == "stat":
        p["options"] = {"reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
                        "colorMode": "background", "graphMode": "area", "textMode": "value_and_name"}
        p["fieldConfig"]["defaults"]["thresholds"] = {"mode": "absolute", "steps": [{"color": "blue", "value": None}]}
    elif kind == "piechart":
        p["options"] = {"reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
                        "pieType": "donut", "legend": {"displayMode": "table", "placement": "right", "values": ["value", "percent"]}}
    return p


CONT = 'name=~"so-.+"'
panels = [
    # Fila 1: indicadores rápidos
    panel("Objetivos arriba (up)", [('sum(up)', "arriba"), ('count(up)', "total")], 0, 0, 6, 5, kind="stat",
          desc="Cuántos targets de Prometheus responden"),
    panel("Solicitudes/s en Nginx", [('sum(rate(nginx_http_requests_total[1m]))', "req/s")], 6, 0, 6, 5, unit="reqps", kind="stat", decimals=1),
    panel("Latencia p95 del backend", [('histogram_quantile(0.95, sum by (le) (rate(app_request_latency_seconds_bucket[1m])))', "p95")], 12, 0, 6, 5, unit="s", kind="stat", decimals=3),
    panel("Conexiones activas en Nginx", [('nginx_connections_active', "activas")], 18, 0, 6, 5, kind="stat"),
    # Fila 2: balanceo
    panel("Solicitudes por segundo por instancia (balanceo)",
          [('sum by (instance_id) (rate(app_requests_total[1m]))', "backend {{instance_id}}")], 0, 5, 12, 9, unit="reqps",
          desc="Si el Round Robin funciona, las tres líneas van juntas"),
    panel("Reparto de solicitudes (últimos 15 min)",
          [('sum by (instance_id) (increase(app_requests_total[15m]))', "backend {{instance_id}}")], 12, 5, 12, 9, kind="piechart", decimals=0),
    # Fila 3: latencia
    panel("Latencia p50 / p95 / p99 por instancia",
          [('histogram_quantile(0.50, sum by (le, instance_id) (rate(app_request_latency_seconds_bucket[1m])))', "p50 backend {{instance_id}}"),
           ('histogram_quantile(0.95, sum by (le, instance_id) (rate(app_request_latency_seconds_bucket[1m])))', "p95 backend {{instance_id}}"),
           ('histogram_quantile(0.99, sum by (le, instance_id) (rate(app_request_latency_seconds_bucket[1m])))', "p99 backend {{instance_id}}")],
          0, 14, 12, 9, unit="s"),
    panel("Latencia promedio por endpoint",
          [('sum by (endpoint) (rate(app_request_latency_seconds_sum[1m])) / sum by (endpoint) (rate(app_request_latency_seconds_count[1m]))', "{{endpoint}}")],
          12, 14, 12, 9, unit="s"),
    # Fila 4: Nginx y errores
    panel("Nginx: conexiones (activas, leyendo, escribiendo, en espera)",
          [('nginx_connections_active', "activas"), ('nginx_connections_reading', "leyendo"),
           ('nginx_connections_writing', "escribiendo"), ('nginx_connections_waiting', "en espera")], 0, 23, 12, 8),
    panel("Respuestas por código HTTP (backend)",
          [('sum by (status) (rate(app_requests_total[1m]))', "HTTP {{status}}")], 12, 23, 12, 8, unit="reqps", stack=True),
    # Fila 5: recursos (cAdvisor)
    panel("CPU por contenedor (% de un núcleo)",
          [(f'sum by (name) (rate(container_cpu_usage_seconds_total{{{CONT}}}[1m])) * 100', "{{name}}")], 0, 31, 12, 9, unit="percent"),
    panel("Memoria por contenedor",
          [(f'sum by (name) (container_memory_working_set_bytes{{{CONT}}})', "{{name}}")], 12, 31, 12, 9, unit="bytes"),
    panel("Red recibida por contenedor",
          [(f'sum by (name) (rate(container_network_receive_bytes_total{{{CONT}}}[1m]))', "{{name}}")], 0, 40, 12, 8, unit="Bps"),
    panel("Solicitudes en curso por instancia",
          [('sum by (instance_id) (app_requests_in_progress)', "backend {{instance_id}}")], 12, 40, 12, 8),
]

dashboard = {
    "uid": "so-infra",
    "title": "Proyecto final SO — Infraestructura Docker",
    "description": "Nginx + 3 backends + Prometheus + cAdvisor",
    "tags": ["docker", "nginx", "prometheus"],
    "timezone": "browser",
    "refresh": "5s",
    "time": {"from": "now-15m", "to": "now"},
    "schemaVersion": 39,
    "version": 1,
    "editable": True,
    "panels": panels,
}

out = Path(__file__).parent / "dashboards" / "infraestructura.json"
out.write_text(json.dumps(dashboard, indent=2, ensure_ascii=False), encoding="utf-8")
print("escrito", out, len(panels), "paneles")
