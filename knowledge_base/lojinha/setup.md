# Lojinha — Setup e Configuração

## URLs de Acesso

| Componente | URL |
|-----------|-----|
| **API base** | `http://165.227.93.41/lojinha` |
| **API versionada** | `http://165.227.93.41/lojinha/v2` |
| **Web App** | `http://165.227.93.41/lojinha-web/v2/` |
| **Swagger UI** | Não confirmado — contrato disponível em `lojinha-api-tests/lojinha-v2.yml` |

> **ATENÇÃO — gotcha crítico:** a baseURL do Playwright deve terminar com `/`
> e incluir o subpath `/lojinha-web/v2/`. Sem isso, navegações relativas como
> `produto/novo` ficam erradas.

## Credenciais Padrão

| Campo | Valor |
|-------|-------|
| `usuarioLogin` | `admin` |
| `usuarioSenha` | `admin` |

Variáveis de ambiente que sobrescrevem os padrões:

| Variável | Padrão | Usado em |
|----------|--------|---------|
| `LOJINHA_BASE_URI` | `http://165.227.93.41/lojinha` | RestAssured (`BaseTest.java`) |
| `LOJINHA_LOGIN` | `admin` | RestAssured (`AuthHelper.java`) |
| `LOJINHA_SENHA` | `admin` | RestAssured (`AuthHelper.java`) |
| `BASE_URL` (k6) | `http://165.227.93.41/lojinha` | k6 (`config.js`) |
| `LOJINHA_LOGIN` | `admin` | k6 (`config.js`) |
| `LOJINHA_SENHA` | `admin` | k6 (`config.js`) |

## Autenticação — Fluxo

```
POST /v2/login
Body: { "usuarioLogin": "admin", "usuarioSenha": "admin" }
→ Response: { "data": { "token": "<jwt>" }, "message": "", "error": "" }
```

O token retornado deve ser passado como **header `token`** (não `Authorization: Bearer`) em todas as chamadas autenticadas.

## Paths Corretos por Projeto

### Playwright (lojinha-tests/)

```typescript
// playwright.config.ts
baseURL: 'http://165.227.93.41/lojinha-web/v2/'

// Navegações relativas:
await page.goto('');            // tela de login
await page.goto('produto');     // lista de produtos
await page.goto('produto/novo');// formulário de novo produto

// URL absoluta necessária para remover produto (barra dupla é intencional na app):
await page.goto('http://165.227.93.41/lojinha-web/v2//produto/remover/${id}');
```

### RestAssured (lojinha-api-tests/)

```java
// BaseTest.java
RestAssured.baseURI = "http://165.227.93.41/lojinha"; // sem /v2 aqui
RestAssured.basePath = "/v2";                          // /v2 no basePath

// Endpoint de login:
POST /login   // não /usuarios/login
```

### k6 (lojinha-performance/k6/)

```javascript
// config.js
BASE_URL = 'http://165.227.93.41/lojinha'

// Requests usam BASE_URL + /v2/...
http.post(`${BASE_URL}/v2/login`, ...)
http.get(`${BASE_URL}/v2/produtos`, ...)
```

## Estrutura de Projetos

```
qa-agents/
├── lojinha-tests/              ← Playwright TypeScript (ARIA)
│   ├── playwright.config.ts
│   ├── pages/
│   │   ├── LoginPage.ts
│   │   ├── ProdutoFormPage.ts
│   │   └── ProdutoListaPage.ts
│   └── tests/
│       ├── login.spec.ts       (5 testes)
│       └── produto.spec.ts     (12 testes)
│
├── lojinha-api-tests/          ← RestAssured Java 17 (NEXUS)
│   ├── build.gradle
│   ├── lojinha-v2.yml          ← OpenAPI spec (fonte de verdade)
│   └── src/test/java/
│       ├── base/BaseTest.java
│       ├── utils/AuthHelper.java
│       └── tests/
│           ├── AuthTest.java   (4 testes)
│           └── ProdutoApiTest.java (13 testes)
│
├── lojinha-performance/        ← k6 + JMeter (FLUX)
│   ├── k6/
│   │   ├── config.js           ← SLAs e credenciais centralizados
│   │   ├── smoke.js
│   │   ├── stress.js
│   │   ├── login-load.js
│   │   └── produtos-load.js
│   └── jmeter/
│       ├── lojinha-smoke.jmx
│       ├── lojinha-load.jmx
│       └── lojinha-stress.jmx
│
└── reports/
    └── relatorio-poc-final.md  ← Relatório executivo SIGMA
```
