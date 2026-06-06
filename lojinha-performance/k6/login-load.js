/**
 * FLUX — Load Test | Endpoint de Login | Lojinha API
 *
 * Foco: medir a capacidade do endpoint de autenticação sob carga sustentada.
 * O login é o gargalo de todas as sessões — se ele cai, o sistema todo cai.
 *
 * Configuração: ramp-up 1min → 10 VUs sustentados 1min → ramp-down 1min
 * SLA crítico: p95 < 300ms (mais restrito que endpoints de dados)
 */
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Counter } from 'k6/metrics';
import { BASE_URL, CREDENTIALS, HEADERS_JSON } from './config.js';

const loginDuration    = new Trend('login_duration_ms', true);
const loginSucessos    = new Counter('login_sucessos');
const loginFalhas      = new Counter('login_falhas');

export const options = {
  stages: [
    { duration: '1m', target: 10 },  // ramp-up gradual
    { duration: '1m', target: 10 },  // carga sustentada
    { duration: '1m', target: 0  },  // ramp-down
  ],
  thresholds: {
    // SLA do login: mais rigoroso — p95 < 300ms
    'http_req_duration{endpoint:login}': ['p(95)<300', 'p(99)<500'],
    http_req_failed: ['rate<0.01'],
    login_duration_ms: ['p(95)<300'],
  },
};

export default function () {
  const res = http.post(
    `${BASE_URL}/v2/login`,
    JSON.stringify(CREDENTIALS),
    { headers: HEADERS_JSON, tags: { endpoint: 'login' } }
  );

  loginDuration.add(res.timings.duration);

  const ok = check(res, {
    'status 200':           (r) => r.status === 200,
    'token no body':        (r) => r.json('data.token') !== null,
    'tempo < 300ms':        (r) => r.timings.duration < 300,
    'Content-Type JSON':    (r) => r.headers['Content-Type'].includes('application/json'),
  });

  ok ? loginSucessos.add(1) : loginFalhas.add(1);

  // Think time realista — usuário não faz login em loop
  sleep(Math.random() * 2 + 1); // 1–3 segundos
}
