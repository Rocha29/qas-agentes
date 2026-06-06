/**
 * FLUX — Smoke Test | Lojinha API
 *
 * Objetivo: confirmar que a API está saudável antes de rodar carga.
 * Regra FLUX: sempre valide o smoke antes do load test.
 *
 * Configuração: 1 usuário virtual, 1 minuto
 * Fluxo completo: login → criar produto → listar → buscar por ID → deletar
 */
import http  from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Rate } from 'k6/metrics';
import { BASE_URL, CREDENTIALS, THRESHOLDS, HEADERS_JSON, headersComToken, payloadProduto } from './config.js';

// Métricas customizadas por etapa do fluxo
const loginDuration   = new Trend('duracao_login',   true);
const criarDuration   = new Trend('duracao_criar',   true);
const listarDuration  = new Trend('duracao_listar',  true);
const buscarDuration  = new Trend('duracao_buscar',  true);
const deletarDuration = new Trend('duracao_deletar', true);
const taxaErro        = new Rate('taxa_erro_negocio');

export const options = {
  stages: [
    { duration: '1m', target: 1 },
  ],
  thresholds: {
    ...THRESHOLDS,
    taxa_erro_negocio: ['rate<0.01'],
  },
};

export default function () {
  const vu  = __VU;
  const iter = __ITER;

  // ─── 1. Login ──────────────────────────────────────────────────────────────
  const resLogin = http.post(
    `${BASE_URL}/v2/login`,
    JSON.stringify(CREDENTIALS),
    { headers: HEADERS_JSON, tags: { endpoint: 'login' } }
  );
  loginDuration.add(resLogin.timings.duration);

  const loginOk = check(resLogin, {
    '[Login] status 200':      (r) => r.status === 200,
    '[Login] token presente':  (r) => r.json('data.token') !== null,
    '[Login] p95 < 300ms':     (r) => r.timings.duration < 300,
  });
  taxaErro.add(!loginOk);

  if (!loginOk) {
    console.error(`[VU${vu}] Login falhou — status ${resLogin.status}`);
    return;
  }

  const token = resLogin.json('data.token');
  const hdrs  = headersComToken(token);

  sleep(0.5);

  // ─── 2. Criar produto ──────────────────────────────────────────────────────
  const resCriar = http.post(
    `${BASE_URL}/v2/produtos`,
    payloadProduto(`VU${vu}-I${iter}`),
    { headers: hdrs, tags: { endpoint: 'produtos' } }
  );
  criarDuration.add(resCriar.timings.duration);

  const criarOk = check(resCriar, {
    '[Criar] status 201':          (r) => r.status === 201,
    '[Criar] produtoId presente':  (r) => r.json('data.produtoId') > 0,
    '[Criar] p95 < 500ms':         (r) => r.timings.duration < 500,
  });
  taxaErro.add(!criarOk);

  if (!criarOk) {
    console.error(`[VU${vu}] Criar produto falhou — status ${resCriar.status} body: ${resCriar.body}`);
    return;
  }

  const produtoId = resCriar.json('data.produtoId');

  sleep(0.3);

  // ─── 3. Listar produtos ────────────────────────────────────────────────────
  const resListar = http.get(
    `${BASE_URL}/v2/produtos`,
    { headers: hdrs, tags: { endpoint: 'produtos' } }
  );
  listarDuration.add(resListar.timings.duration);

  check(resListar, {
    '[Listar] status 200':      (r) => r.status === 200,
    '[Listar] lista não vazia': (r) => r.json('data').length > 0,
    '[Listar] p95 < 500ms':     (r) => r.timings.duration < 500,
  });

  sleep(0.3);

  // ─── 4. Buscar produto por ID ──────────────────────────────────────────────
  const resBuscar = http.get(
    `${BASE_URL}/v2/produtos/${produtoId}`,
    { headers: hdrs, tags: { endpoint: 'produtos' } }
  );
  buscarDuration.add(resBuscar.timings.duration);

  check(resBuscar, {
    '[Buscar] status 200':    (r) => r.status === 200,
    '[Buscar] ID correto':    (r) => r.json('data.produtoId') === produtoId,
    '[Buscar] p95 < 500ms':   (r) => r.timings.duration < 500,
  });

  sleep(0.3);

  // ─── 5. Deletar produto ────────────────────────────────────────────────────
  const resDeletar = http.del(
    `${BASE_URL}/v2/produtos/${produtoId}`,
    null,
    { headers: hdrs, tags: { endpoint: 'produtos' } }
  );
  deletarDuration.add(resDeletar.timings.duration);

  const deletarOk = check(resDeletar, {
    '[Deletar] status 204': (r) => r.status === 204,
    '[Deletar] p95 < 500ms':(r) => r.timings.duration < 500,
  });
  taxaErro.add(!deletarOk);

  sleep(1);
}
