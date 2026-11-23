// Prueba de carga con k6 contra Nginx (puerto publicado en el host).
// Uso:  k6 run k6/prueba-carga.js
//   o, sin instalar k6 (PowerShell, desde la raíz del proyecto):
//        docker run --rm -e BASE_URL=http://host.docker.internal:8080 -v ${PWD}/k6:/scripts/k6 -w /scripts grafana/k6:1.4.2 run --quiet k6/prueba-carga.js
import http from "k6/http";
import { check, sleep } from "k6";
import { Counter } from "k6/metrics";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8080";
const porInstancia = new Counter("respuestas_por_instancia");

export const options = {
  stages: [
    { duration: "30s", target: 10 },  // calentamiento
    { duration: "1m", target: 30 },   // carga normal
    { duration: "1m", target: 60 },   // carga alta
    { duration: "30s", target: 0 },   // bajada
  ],
  thresholds: {
    http_req_failed: ["rate<0.01"],               // menos del 1 % de errores
    http_req_duration: ["p(95)<500"],             // el 95 % responde en menos de 500 ms
  },
};

export default function () {
  // 70 % de las veces la página principal (rápida) y 30 % una operación de CPU.
  const url = Math.random() < 0.7 ? `${BASE_URL}/` : `${BASE_URL}/api/trabajo?ms=40`;
  const res = http.get(url);
  check(res, {
    "status 200": (r) => r.status === 200,
    "responde una instancia": (r) => !!r.headers["X-Backend-Instance"],
  });
  porInstancia.add(1, { instancia: res.headers["X-Backend-Instance"] || "ninguna" });
  sleep(0.2);
}

export function handleSummary(data) {
  return {
    "k6/resultado.json": JSON.stringify(data, null, 2),
    stdout: textSummary(data),
  };
}

function textSummary(data) {
  const m = data.metrics;
  const d = m.http_req_duration.values;
  const lines = [
    "",
    "===== Resumen de la prueba de carga =====",
    `Solicitudes totales : ${m.http_reqs.values.count}`,
    `Solicitudes/s       : ${m.http_reqs.values.rate.toFixed(1)}`,
    `Errores             : ${(m.http_req_failed.values.rate * 100).toFixed(2)} %`,
    `Latencia promedio   : ${d.avg.toFixed(1)} ms`,
    `Latencia p90 / p95  : ${d["p(90)"].toFixed(1)} / ${d["p(95)"].toFixed(1)} ms`,
    `Latencia máxima     : ${d.max.toFixed(1)} ms`,
    `Usuarios virtuales  : hasta ${m.vus_max.values.max}`,
    "",
  ];
  return lines.join("\n");
}
