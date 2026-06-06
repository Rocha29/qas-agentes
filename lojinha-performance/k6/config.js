// Configuração central — altere aqui para apontar a outro ambiente
export const BASE_URL = __ENV.BASE_URL || 'http://165.227.93.41/lojinha';

export const CREDENTIALS = {
  usuarioLogin: __ENV.LOJINHA_LOGIN || 'admin',
  usuarioSenha: __ENV.LOJINHA_SENHA || 'admin',
};

// SLAs definidos pelo FLUX (Pessoni: percentis, nunca médias)
export const THRESHOLDS = {
  // Globais — todos os endpoints
  http_req_duration: ['p(95)<500', 'p(99)<1000'],
  http_req_failed:   ['rate<0.01'],

  // Login deve ser mais rápido — é o gargalo de sessão
  'http_req_duration{endpoint:login}':   ['p(95)<300'],
  'http_req_duration{endpoint:produtos}': ['p(95)<500'],
};

export const HEADERS_JSON = { 'Content-Type': 'application/json' };

export function headersComToken(token) {
  return { 'Content-Type': 'application/json', token };
}

export function payloadProduto(sufixo) {
  return JSON.stringify({
    produtoNome:    `FLUX-Produto-${sufixo}`,
    produtoValor:   250,
    produtoCores:   ['preto'],
    produtoUrlMock: '',
    componentes: [{ componenteNome: 'Item FLUX', componenteQuantidade: 1 }],
  });
}
