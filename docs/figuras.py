"""Genera las figuras del informe: diagrama de arquitectura, capturas de terminal
(salidas reales de comandos) y la vista de cAdvisor de un backend.

Uso (con el stack arriba): python docs/figuras.py
"""
import html
import subprocess
import time
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
IMG = RAIZ / "docs" / "img"


def sh(cmd):
    r = subprocess.run(cmd, shell=True, cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return (r.stdout + r.stderr).rstrip()


TERMINAL = """<html><body style="margin:0;background:#0c0c0c">
<div style="font:15px/1.45 Consolas,monospace;color:#d4d4d4;padding:18px 22px;white-space:pre">{cuerpo}</div></body></html>"""


def terminal_html(bloques):
    partes = []
    for cmd, salida in bloques:
        partes.append(f'<span style="color:#4ec9b0">PS C:\\so-proyecto-final&gt;</span> <span style="color:#fff">{html.escape(cmd)}</span>\n{html.escape(salida)}\n')
    return TERMINAL.format(cuerpo="\n".join(partes))


ARQ = """<html><body style="margin:0;background:#fff;font-family:Segoe UI,Arial">
<svg width="1500" height="760" viewBox="0 0 1500 760" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="f" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#475569"/></marker>
<marker id="g" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#c2410c"/></marker></defs>
<style>.b{rx:12;stroke-width:2}.t{font-size:20px;font-weight:600;fill:#0f172a}.s{font-size:15px;fill:#334155}.l{stroke:#475569;stroke-width:2.2;fill:none;marker-end:url(#f)}.m{stroke:#c2410c;stroke-width:2;fill:none;stroke-dasharray:7 5;marker-end:url(#g)}</style>
<rect x="15" y="60" width="1470" height="685" rx="18" fill="#f8fafc" stroke="#94a3b8" stroke-dasharray="8 6" stroke-width="2"/>
<text x="35" y="92" class="t" fill="#475569">Red Docker «so_monitoreo» (bridge)</text>
<rect x="30" y="300" width="190" height="110" class="b" fill="#e0f2fe" stroke="#0369a1"/>
<text x="125" y="340" text-anchor="middle" class="t">Host / k6</text><text x="125" y="368" text-anchor="middle" class="s">navegador y</text><text x="125" y="390" text-anchor="middle" class="s">prueba de carga</text>
<rect x="300" y="290" width="230" height="130" class="b" fill="#dcfce7" stroke="#15803d"/>
<text x="415" y="330" text-anchor="middle" class="t">Nginx</text><text x="415" y="358" text-anchor="middle" class="s">proxy inverso + Round Robin</text><text x="415" y="382" text-anchor="middle" class="s">:8080 → :80 · stub_status :8088</text>
<g><rect x="640" y="130" width="230" height="95" class="b" fill="#fef9c3" stroke="#a16207"/><text x="755" y="168" text-anchor="middle" class="t">backend1</text><text x="755" y="195" text-anchor="middle" class="s">Flask :5000 · /metrics</text></g>
<g><rect x="640" y="308" width="230" height="95" class="b" fill="#fef9c3" stroke="#a16207"/><text x="755" y="346" text-anchor="middle" class="t">backend2</text><text x="755" y="373" text-anchor="middle" class="s">Flask :5000 · /metrics</text></g>
<g><rect x="640" y="486" width="230" height="95" class="b" fill="#fef9c3" stroke="#a16207"/><text x="755" y="524" text-anchor="middle" class="t">backend3</text><text x="755" y="551" text-anchor="middle" class="s">Flask :5000 · /metrics</text></g>
<rect x="300" y="560" width="230" height="95" class="b" fill="#fee2e2" stroke="#b91c1c"/><text x="415" y="598" text-anchor="middle" class="t">nginx-exporter</text><text x="415" y="625" text-anchor="middle" class="s">:9113 (interno)</text>
<rect x="1000" y="130" width="230" height="95" class="b" fill="#fee2e2" stroke="#b91c1c"/><text x="1115" y="168" text-anchor="middle" class="t">cAdvisor</text><text x="1115" y="195" text-anchor="middle" class="s">CPU, memoria, red · :8081</text>
<rect x="1000" y="380" width="230" height="110" class="b" fill="#ede9fe" stroke="#6d28d9"/><text x="1115" y="420" text-anchor="middle" class="t">Prometheus</text><text x="1115" y="447" text-anchor="middle" class="s">scrape cada 5 s · :9090</text><text x="1115" y="470" text-anchor="middle" class="s">volumen prometheus_data</text>
<rect x="1000" y="590" width="230" height="110" class="b" fill="#ffedd5" stroke="#c2410c"/><text x="1115" y="630" text-anchor="middle" class="t">Grafana</text><text x="1115" y="657" text-anchor="middle" class="s">dashboards · :3000</text><text x="1115" y="680" text-anchor="middle" class="s">volumen grafana_data</text>
<path d="M220,355 L298,355" class="l"/>
<path d="M530,330 C590,300 590,178 638,178" class="l"/><path d="M530,355 L638,355" class="l"/><path d="M530,380 C590,410 590,533 638,533" class="l"/>
<path d="M415,420 L415,558" class="m"/>
<path d="M998,420 C930,400 930,190 872,178" class="m"/><path d="M998,430 L872,360" class="m"/><path d="M998,445 C930,470 930,533 872,533" class="m"/>
<path d="M998,470 C760,700 650,640 532,610" class="m"/>
<path d="M1115,378 L1115,227" class="m"/>
<path d="M1115,588 L1115,492" class="m"/>
<text x="1250" y="300" class="s" fill="#c2410c">— — scrape / consulta</text><text x="1250" y="325" class="s">——  tráfico HTTP</text>
<text x="750" y="40" text-anchor="middle" style="font-size:26px;font-weight:700;fill:#0f172a">Arquitectura del proyecto (docker compose)</text>
</svg></body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1500, "height": 760})
    pg.set_content(ARQ)
    pg.screenshot(path=str(IMG / "00-arquitectura.png"))

    def term(nombre, bloques, ancho=1300):
        pg.set_viewport_size({"width": ancho, "height": 200})
        pg.set_content(terminal_html(bloques))
        pg.screenshot(path=str(IMG / nombre), full_page=True)
        print("ok", nombre)

    term("10-compose-ps.png", [("docker compose ps", sh('docker compose ps --format "table {{.Name}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}"'))], 1500)
    import urllib.request
    curl = "\n".join(urllib.request.urlopen("http://localhost:8080/").read().decode() for _ in range(6))
    term("11-balanceo-curl.png", [("1..6 | % { curl.exe -s http://localhost:8080/ }", curl)])
    term("12-metricas.png", [
        ("docker compose exec nginx wget -qO- http://127.0.0.1:8088/stub_status", sh("docker compose exec -T nginx wget -qO- http://127.0.0.1:8088/stub_status")),
        ("docker compose exec nginx wget -qO- http://backend1:5000/metrics | Select-String '^app_requests_total'",
         "\n".join(l for l in sh("docker compose exec -T nginx wget -qO- http://backend1:5000/metrics").splitlines() if l.startswith("app_requests_total"))),
    ])
    k6 = (RAIZ / "docs" / "k6-salida.txt").read_text(encoding="utf-8").strip()
    term("13-k6.png", [("docker run --rm -e BASE_URL=http://host.docker.internal:8080 -v ${PWD}/k6:/scripts/k6 -w /scripts grafana/k6:1.4.2 run --quiet k6/prueba-carga.js", k6)])

    # cAdvisor: vista de un solo backend (sin mostrar otros contenedores del equipo)
    pg.set_viewport_size({"width": 1600, "height": 1500})
    pg.goto("http://localhost:8081/docker/so-backend1", wait_until="load")
    time.sleep(6)
    pg.screenshot(path=str(IMG / "04-cadvisor.png"))
    b.close()

im = Image.open(IMG / "04-cadvisor.png")
if im.size[0] > 1200:  # solo la primera vez (la imagen original mide 1600 px)
    im = im.crop((230, 0, 1370, 1500))
im.crop((0, 430, im.size[0], 1400)).save(IMG / "04-cadvisor.png")

# Las tres respuestas del navegador (de capturas.py) en una sola imagen
if (IMG / "01-nginx-respuesta-1.png").exists():
    partes = [Image.open(IMG / f"01-nginx-respuesta-{n}.png").crop((0, 0, 1100, 60)) for n in (1, 2, 3)]
    lienzo = Image.new("RGB", (1100, 180), "white")
    for i, im in enumerate(partes):
        lienzo.paste(im, (0, i * 60))
    lienzo.save(IMG / "01-nginx-navegador.png")
    for n in (1, 2, 3):
        (IMG / f"01-nginx-respuesta-{n}.png").unlink()
print("figuras listas")
