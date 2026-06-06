/**
 * FLUX — Load Test | CRUD de Produtos | Lojinha API
 *
 * Simula o fluxo completo de um usuário autenticado:
 * login → criar produto → listar → buscar por ID → deletar
 *
 * Setup: token obtido uma vez por VU (setUp paralelo mais realista)
 * Configuração: ramp-up 1min → 10 VUs sustentados 1min → ramp-down 1min
 */
import http  from 'k6/http';
import { check, sleep, group } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';
import { BASE_URL, CREDENTIALS, HEADERS_JSON, headersComToken, payloadProduto } from './config.js';

// Métricas por operação — FLUX: percentis por endpoint, nunca média geral
const mLogin    = new Trend('op_login_ms',   true);
const mCriar    = new Trend('op_criar_ms',   true);
const mListar   = new Trend('op_listar_ms',  true);
const mBuscar   = new Trend('op_buscar_ms',  true);
const mDeletar  = new Trend('op_deletar_ms', true);
const erroNeg   = new Rate('erro_negocio');
const iterOk    = new Counter('iteracoes_completas');

export const options = {
  stages: [
    { duration: '1m', target: 10 },
    { duration: '1m', target: 10 },
    { duration: '1m', target: 0  },
  ],
  thresholds: {
    'http_req_duration{endpoint:login}':   ['p(95)<300'],
    'http_req_duration{endpoint:produtos}':['p(95)<500'],
    http_req_failed: ['rate<0.01'],
    erro_negocio:    ['rate<0.01'],
    op_login_ms:     ['p(95)<300'],
    op_criar_ms:     ['p(95)<500'],
    op_listar_ms:    ['p(95)<500'],
    op_buscar_ms:    ['p(95)<500'],
    op_deletar_ms:   ['p(95)<500'],
  },
};

export default function () {
  let token, produtoId;

  // ─── Login ─────────────────────────────────────────────────────────────────
  group('1_login', () => {
    const r = http.post(
      `${BASE_URL}/v2/login`,
      JSON.stringify(CREDENTIALS),
      { headers: HEADERS_JSON, tags: { endpoint: 'login' } }
    );
    mLogin.add(r.timings.duration);

    const ok = check(r, {
      'login 200':     (r) => r.status === 200,
      'token ok':      (r) => !!r.json('data.token'),
    });
    erroNeg.add(!ok);
    if (!ok) return;
    token = r.json('data.token');
  });

  if (!token) return;

  const hdrs = headersComToken(token);

  sleep(0.5);

  // ─── Criar produto ─────────────────────────────────────────────────────────
  group('2_criar_produto', () => {
    const r = http.post(
      `${BASE_URL}/v2/produtos`,
      payloadProduto(`VU${__VU}-${__ITER}`),
      { headers: hdrs, tags: { endpoint: 'produtos' } }
    );
    mCriar.add(r.timings.duration);

    const ok = check(r, {
      'criar 201':    (r) => r.status === 201,
      'id presente':  (r) => r.json('data.produtoId') > 0,
    });
    erroNeg.add(!ok);
    if (ok) produtoId = r.json('data.produtoId');
  });

  if (!produtoId) return;

  sleep(0.3);

  // ─── Listar produtos ───────────────────────────────────────────────────────
  group('3_listar_produtos', () => {
    const r = http.get(
      `${BASE_URL}/v2/produtos`,
      { headers: hdrs, tags: { endpoint: 'produtos' } }
    );
    mListar.add(r.timings.duration);
    check(r, { 'listar 200': (r) => r.status === 200 });
  });

  sleep(0.3);

  // ─── Buscar por ID ─────────────────────────────────────────────────────────
  group('4_buscar_produto', () => {
    const r = http.get(
      `${BASE_URL}/v2/produtos/${produtoId}`,
      { headers: hdrs, tags: { endpoint: 'produtos' } }
    );
    mBuscar.add(r.timings.duration);
    check(r, {
      'buscar 200':   (r) => r.status === 200,
      'id correto':   (r) => r.json('data.produtoId') === produtoId,
    });
  });

  sleep(0.3);

  // ─── Deletar produto ───────────────────────────────────────────────────────
  group('5_deletar_produto', () => {
    const r = http.del(
      `${BASE_URL}/v2/produtos/${produtoId}`,
      null,
      { headers: hdrs, tags: { endpoint: 'produtos' } }
    );
    mDeletar.add(r.timings.duration);

    const ok = check(r, { 'deletar 204': (r) => r.status === 204 });
    erroNeg.add(!ok);
    if (ok) iterOk.add(1);
  });

  sleep(1);
}
