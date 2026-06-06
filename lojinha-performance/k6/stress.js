/**
 * FLUX — Stress Test | Lojinha API
 *
 * Objetivo: encontrar o ponto de saturação — onde a API começa a degradar.
 * Estratégia: escada de carga, +5 VUs a cada 30s, de 5 até 50.
 *
 * FLUX rule: Stress test NÃO deve rodar em produção sem aviso prévio.
 * Use em ambiente de homologação ou com janela de manutenção acordada.
 *
 * Interprete os resultados assim:
 *   - Até onde o p95 se mantém < 500ms? → zona segura
 *   - Em que patamar o erro rate sobe?  → ponto de saturação
 *   - A API se recupera após ramp-down? → elasticidade
 */
import http  from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Rate } from 'k6/metrics';
import { BASE_URL, CREDENTIALS, HEADERS_JSON, headersComToken, payloadProduto } from './config.js';

const durTotal  = new Trend('stress_duracao_total_ms', true);
const erroRate  = new Rate('stress_erro');

export const options = {
  stages: [
    { duration: '30s', target: 5  },  // aquecimento
    { duration: '30s', target: 10 },  // +5 VUs
    { duration: '30s', target: 15 },
    { duration: '30s', target: 20 },
    { duration: '30s', target: 25 },
    { duration: '30s', target: 30 },
    { duration: '30s', target: 35 },
    { duration: '30s', target: 40 },
    { duration: '30s', target: 45 },
    { duration: '30s', target: 50 },  // pico máximo
    { duration: '1m',  target: 50 },  // sustentação no limite
    { duration: '1m',  target: 0  },  // recuperação
  ],
  // Stress: thresholds mais permissivos — o objetivo é encontrar o limite, não passar
  thresholds: {
    http_req_failed:      ['rate<0.05'],   // até 5% de erro é informação útil
    stress_erro:          ['rate<0.05'],
    http_req_duration:    ['p(95)<2000'],  // 2s no pico — queremos ver onde quebra
  },
};

export default function () {
  const inicio = Date.now();

  // Login
  const rLogin = http.post(
    `${BASE_URL}/v2/login`,
    JSON.stringify(CREDENTIALS),
    { headers: HEADERS_JSON, tags: { endpoint: 'login' } }
  );

  const loginOk = check(rLogin, { 'login 200': (r) => r.status === 200 });
  erroRate.add(!loginOk);

  if (!loginOk) {
    console.warn(`[STRESS VU${__VU}] Login falhou com ${rLogin.status} — registrando degradação`);
    sleep(1);
    return;
  }

  const token = rLogin.json('data.token');
  const hdrs  = headersComToken(token);

  // Criar produto
  const rCriar = http.post(
    `${BASE_URL}/v2/produtos`,
    payloadProduto(`STR-VU${__VU}-${__ITER}`),
    { headers: hdrs, tags: { endpoint: 'produtos' } }
  );

  const criarOk = check(rCriar, { 'criar 201': (r) => r.status === 201 });
  erroRate.add(!criarOk);

  if (criarOk) {
    const id = rCriar.json('data.produtoId');

    // GET por ID
    const rBuscar = http.get(
      `${BASE_URL}/v2/produtos/${id}`,
      { headers: hdrs, tags: { endpoint: 'produtos' } }
    );
    check(rBuscar, { 'buscar 200': (r) => r.status === 200 });

    // DELETE — limpeza (evita acúmulo de dados no servidor de teste)
    const rDel = http.del(
      `${BASE_URL}/v2/produtos/${id}`,
      null,
      { headers: hdrs, tags: { endpoint: 'produtos' } }
    );
    const delOk = check(rDel, { 'deletar 204': (r) => r.status === 204 });
    erroRate.add(!delOk);
  }

  durTotal.add(Date.now() - inicio);
  sleep(0.5);
}
