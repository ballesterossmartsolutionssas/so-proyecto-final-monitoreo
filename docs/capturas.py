"""Toma las capturas del informe con Playwright (Chromium sin interfaz).

Uso: python docs/capturas.py "2026-11-22 23:29" "2026-11-22 23:37"
(el rango de tiempo es el de la prueba de carga, en hora local)
"""
import sys
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

IMG = Path(__file__).parent / "img"
IMG.mkdir(exist_ok=True)
desde = int(datetime.strptime(sys.argv[1], "%Y-%m-%d %H:%M").timestamp() * 1000)
hasta = int(datetime.strptime(sys.argv[2], "%Y-%m-%d %H:%M").timestamp() * 1000)


def foto(page, url, nombre, espera=3, alto=None, full=False):
    page.goto(url, wait_until="load")
    time.sleep(espera)
    if alto:
        page.set_viewport_size({"width": 1600, "height": alto})
        time.sleep(1)
    page.screenshot(path=str(IMG / nombre), full_page=full)
    print("ok", nombre)


with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1600, "height": 900}, device_scale_factor=1)

    # 1) La aplicación a través de Nginx (tres recargas: muestra que cambia la instancia)
    page.set_viewport_size({"width": 1100, "height": 260})
    for n in (1, 2, 3):
        foto(page, "http://localhost:8080/", f"01-nginx-respuesta-{n}.png", espera=0.5)

    # 2) Prometheus: estado de los targets
    page.set_viewport_size({"width": 1600, "height": 900})
    foto(page, "http://localhost:9090/targets", "02-prometheus-targets.png", espera=3, full=True)

    # 3) Prometheus: consulta de solicitudes por instancia en el rango de la prueba
    q = "sum%20by%20(instance_id)%20(rate(app_requests_total%5B1m%5D))"
    end = hasta / 1000
    rng = int((hasta - desde) / 1000)
    foto(page, f"http://localhost:9090/query?g0.expr={q}&g0.tab=graph&g0.range_input={rng}s&g0.end_input={time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(end))}Z",
         "03-prometheus-consulta.png", espera=4)

    # 4) cAdvisor: página de contenedores Docker
    foto(page, "http://localhost:8081/docker/", "04-cadvisor.png", espera=3)

    # 5) Grafana: dashboard completo en modo kiosco con el rango de la prueba
    page.set_viewport_size({"width": 1600, "height": 2700})
    foto(page, f"http://localhost:3000/d/so-infra/?orgId=1&from={desde}&to={hasta}&kiosk&refresh=", "05-grafana-dashboard.png", espera=8)
    b.close()
