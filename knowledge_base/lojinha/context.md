# Contexto da Lojinha API — Gerado automaticamente por rag_loader.py
# Injete este arquivo no início de qualquer sessão para recarregar o contexto completo.
# Fonte: knowledge_base/lojinha/

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

---
<!-- Fonte: ambiente.md -->

# Lojinha — Ambiente, Dependências e Comandos

## Pré-requisitos do Sistema

| Ferramenta | Versão mínima | Verificar com |
|-----------|--------------|---------------|
| Node.js | 18+ | `node --version` |
| Java | 17 | `java --version` |
| Gradle | 8.7 (wrapper incluso) | `./gradlew --version` |
| k6 | qualquer recente | `k6 version` |
| JMeter | 5.x | `jmeter --version` |
| Playwright browsers | automático | `npx playwright install` |

---

## Projeto 1 — lojinha-tests/ (Playwright TypeScript)

### Dependências (package.json)

```json
{
  "devDependencies": {
    "@playwright/test": "^1.60.0",
    "typescript": "^6.0.3"
  }
}
```

### Setup

```bash
cd lojinha-tests
npm install
npx playwright install chromium   # instalar browser
```

### Executar testes

```bash
# Todos os testes
npx playwright test

# Só login
npx playwright test tests/login.spec.ts

# Só produto
npx playwright test tests/produto.spec.ts

# Com interface visual (headed)
npx playwright test --headed

# Relatório HTML após execução
npx playwright show-report
```

### Configuração (playwright.config.ts)

```typescript
baseURL:    'http://165.227.93.41/lojinha-web/v2/'  // com barra final
testDir:    './tests'
browser:    chromium (Desktop Chrome)
parallel:   false (testes sequenciais — estado compartilhado)
retries:    0
screenshot: only-on-failure
video:      retain-on-failure
trace:      retain-on-failure
```

---

## Projeto 2 — lojinha-api-tests/ (RestAssured Java 17)

### Dependências (build.gradle)

```groovy
testImplementation 'io.rest-assured:rest-assured:5.4.0'
testImplementation 'io.rest-assured:json-path:5.4.0'
testImplementation 'io.rest-assured:json-schema-validator:5.4.0'
testImplementation 'org.junit.jupiter:junit-jupiter:5.10.2'
testImplementation 'com.fasterxml.jackson.core:jackson-databind:2.17.0'
testImplementation 'org.assertj:assertj-core:3.25.3'
testRuntimeOnly  'org.junit.platform:junit-platform-launcher'
```

### Setup

```bash
cd lojinha-api-tests
# Gradle wrapper já está incluído — não precisa instalar Gradle separado
chmod +x gradlew
```

### Executar testes

```bash
# Todos os testes
./gradlew test

# Com output detalhado
./gradlew test --info

# Apenas uma classe
./gradlew test --tests "tests.AuthTest"
./gradlew test --tests "tests.ProdutoApiTest"

# Relatório HTML gerado em:
# build/reports/tests/test/index.html
```

### Variáveis de ambiente (opcionais)

```bash
# Apontar para outro ambiente
export LOJINHA_BASE_URI=http://outro-servidor/lojinha
export LOJINHA_LOGIN=meu_usuario
export LOJINHA_SENHA=minha_senha

./gradlew test
```

### Estrutura de arquivos relevantes

```
lojinha-api-tests/
├── build.gradle
├── settings.gradle
├── lojinha-v2.yml                          ← OpenAPI spec
├── gradle/wrapper/gradle-wrapper.properties ← Gradle 8.7
└── src/test/
    ├── java/
    │   ├── base/BaseTest.java              ← configuração RestAssured
    │   ├── utils/AuthHelper.java           ← helper de autenticação
    │   └── tests/
    │       ├── AuthTest.java               (4 testes)
    │       └── ProdutoApiTest.java         (13 testes — CRUD + validações)
    └── resources/
        └── schemas/produto-schema.json     ← JSON Schema Draft-07
```

---

## Projeto 3 — lojinha-performance/ (k6 + JMeter)

### k6

#### Instalação (macOS)

```bash
brew install k6
```

#### Arquivos

```
lojinha-performance/k6/
├── config.js       ← SLAs, credenciais, BASE_URL, helpers
├── smoke.js        ← 1 VU, 1 min — fluxo completo
├── stress.js       ← rampa crescente de carga
├── login-load.js   ← foco no endpoint de login
└── produtos-load.js← foco nos endpoints de produto
```

#### Executar

```bash
# Smoke test (sempre primeiro)
k6 run lojinha-performance/k6/smoke.js

# Com outro ambiente
k6 run -e BASE_URL=http://outro/lojinha lojinha-performance/k6/smoke.js

# Stress test
k6 run lojinha-performance/k6/stress.js

# Salvar resultados
k6 run --out json=results.json lojinha-performance/k6/smoke.js
```

#### SLAs configurados (config.js)

| Threshold | Valor |
|-----------|-------|
| p95 global | < 500ms |
| p99 global | < 1000ms |
| taxa de erro | < 1% |
| p95 login | < 300ms |
| p95 produtos | < 500ms |

---

### JMeter

#### Instalação (macOS)

```bash
brew install jmeter
```

#### Arquivos

```
lojinha-performance/jmeter/
├── lojinha-smoke.jmx   ← smoke (1 thread, 1 loop)
├── lojinha-load.jmx    ← carga moderada
├── lojinha-stress.jmx  ← stress (rampa)
├── lojinha-test-plan.jmx
└── results/
    ├── smoke-aggregate.csv
    └── smoke-report/   ← relatório HTML
```

#### Executar

```bash
# Smoke test em modo headless
jmeter -n \
  -t lojinha-performance/jmeter/lojinha-smoke.jmx \
  -l lojinha-performance/jmeter/results/smoke-results.jtl \
  -e -o lojinha-performance/jmeter/results/smoke-report/

# Abrir GUI para editar planos
jmeter
```

#### Resultado observado — smoke

| Métrica | Valor | SLA | Status |
|---------|-------|-----|--------|
| p95 geral | 475ms | <500ms | ✅ |
| Taxa de erro | 4,44% | <1% | ❌ |

> Erro relacionado ao BUG #2 (sem paginação). Corrigir antes de usar JMeter como baseline.

---

## Resultado Final da POC (referência rápida)

| Camada | Testes | Resultado |
|--------|--------|-----------|
| Web (Playwright) | 17 | ✅ 17/17 passando |
| API (RestAssured) | 17 | ✅ 17/17 passando |
| Performance (k6) | smoke | ✅ 4/5 endpoints dentro do SLA |
| Performance (JMeter) | smoke | ⚠️ p95 ok, taxa erro 4,44% |

---
<!-- Fonte: endpoints.md -->

# Lojinha — Endpoints Mapeados

**Host:** `165.227.93.41`
**Base path:** `/lojinha`
**Versão:** `v2`
**Protocolo:** HTTP (sem TLS)
**Fonte:** `lojinha-api-tests/lojinha-v2.yml`

---

## Resumo

| Método | Endpoint | Auth | Descrição |
|--------|----------|------|-----------|
| POST | `/v2/login` | ❌ | Autenticar e obter token |
| POST | `/v2/usuarios` | ❌ | Criar novo usuário |
| DELETE | `/v2/dados` | ✅ | Limpar todos os dados do usuário |
| POST | `/v2/produtos` | ✅ | Criar produto |
| GET | `/v2/produtos` | ✅ | Listar produtos (com filtros opcionais) |
| GET | `/v2/produtos/{id}` | ✅ | Buscar produto por ID |
| PUT | `/v2/produtos/{id}` | ✅ | Atualizar produto |
| DELETE | `/v2/produtos/{id}` | ✅ | Remover produto |
| POST | `/v2/produtos/{id}/componentes` | ✅ | Adicionar componente |
| GET | `/v2/produtos/{id}/componentes/{cid}` | ✅ | Buscar componente |
| PUT | `/v2/produtos/{id}/componentes/{cid}` | ✅ | Atualizar componente |
| DELETE | `/v2/produtos/{id}/componentes/{cid}` | ✅ | Remover componente |

---

## Detalhes por Endpoint

### POST /v2/login

**Auth:** não requer token

**Request body:**
```json
{
  "usuarioLogin": "admin",
  "usuarioSenha": "admin"
}
```

**Response 200:**
```json
{
  "data": { "token": "<string>" },
  "message": "",
  "error": ""
}
```

**Responses:** `200` OK, `401` Unauthorized

---

### POST /v2/usuarios

**Auth:** não requer token

**Request body:**
```json
{
  "usuarioNome": "string",
  "usuarioLogin": "string",
  "usuarioSenha": "string"
}
```

**Response 201:**
```json
{
  "data": { "usuarioId": 1, "usuarioLogin": "string", "usuarioNome": "string" },
  "message": "",
  "error": ""
}
```

**Responses:** `201` Created, `400` Bad Request, `409` Conflict (login duplicado)

---

### DELETE /v2/dados

**Auth:** `token` header obrigatório

**Response:** `204` No Content, `401` Unauthorized

> Apaga todos os produtos e componentes do usuário autenticado. Usado para reset de estado em testes.

---

### POST /v2/produtos

**Auth:** `token` header obrigatório

**Request body:**
```json
{
  "produtoNome": "string",
  "produtoValor": 4999,
  "produtoCores": ["preto", "prata"],
  "produtoUrlMock": "",
  "componentes": [
    { "componenteNome": "string", "componenteQuantidade": 1 }
  ]
}
```

**Campos obrigatórios:** `produtoNome`, `produtoValor`, `componentes`

**Regras de negócio:**
- `produtoValor`: inteiro, mínimo 1, máximo 7000 — valor 0 retorna 422
- `componentes`: array obrigatório, mínimo 1 item
- `componenteQuantidade`: inteiro ≥ 1

**Response 201:**
```json
{
  "data": {
    "produtoId": 1,
    "produtoNome": "string",
    "produtoValor": 4999,
    "produtoCores": ["preto"],
    "produtoUrlMock": "",
    "componentes": [{ "componenteId": 1, "componenteNome": "string", "componenteQuantidade": 1 }]
  },
  "message": "",
  "error": ""
}
```

**Responses:** `201` Created, `400` Bad Request, `401` Unauthorized, `422` Unprocessable Entity

> **BUG #1:** token inválido retorna `500` em vez de `401`

---

### GET /v2/produtos

**Auth:** `token` header obrigatório

**Query params (opcionais):**
- `produtoNome` — filtro por nome (string)
- `produtoCores` — filtro por cor (string)

**Response 200:**
```json
{
  "data": [ /* array de Produto */ ],
  "message": "",
  "error": ""
}
```

**Responses:** `200` OK, `401` Unauthorized

> **BUG #2:** sem paginação. Com dados acumulados retorna 41KB e viola SLA de 500ms com 1 usuário (604ms observado).

---

### GET /v2/produtos/{produtoId}

**Auth:** `token` header obrigatório

**Path param:** `produtoId` (integer)

**Response 200:** objeto `ProdutoResponse` (mesmo schema do POST)

**Responses:** `200` OK, `401` Unauthorized, `404` Not Found

---

### PUT /v2/produtos/{produtoId}

**Auth:** `token` header obrigatório

**Body:** mesmo schema do POST

**Responses:** `200` OK, `400` Bad Request, `401` Unauthorized, `422` Unprocessable Entity

---

### DELETE /v2/produtos/{produtoId}

**Auth:** `token` header obrigatório

**Response:** `204` No Content

**Responses:** `204` No Content, `401` Unauthorized, `404` Not Found

---

### POST /v2/produtos/{produtoId}/componentes

**Auth:** `token` header obrigatório

**Request body:**
```json
{ "componenteNome": "string", "componenteQuantidade": 1 }
```

**Response 201:** objeto `ComponenteResponse`

**Responses:** `201` Created, `401` Unauthorized

---

### GET /v2/produtos/{produtoId}/componentes/{componenteId}

**Auth:** `token` header obrigatório

**Response 200:** objeto `ComponenteResponse`

**Responses:** `200` OK, `401` Unauthorized, `404` Not Found

---

### PUT /v2/produtos/{produtoId}/componentes/{componenteId}

**Auth:** `token` header obrigatório

**Body:** `ComponenteRequest` (`componenteNome`, `componenteQuantidade`)

**Responses:** `200` OK, `401` Unauthorized

---

### DELETE /v2/produtos/{produtoId}/componentes/{componenteId}

**Auth:** `token` header obrigatório

**Response:** `204` No Content

**Responses:** `204` No Content, `401` Unauthorized, `404` Not Found

---

## Schemas de Dados

### ProdutoRequest (POST/PUT)

```json
{
  "produtoNome":   "string (obrigatório)",
  "produtoValor":  "integer, 1–7000 (obrigatório)",
  "produtoCores":  ["string"],
  "produtoUrlMock":"string",
  "componentes":   [{ "componenteNome": "string", "componenteQuantidade": "integer ≥1" }]
}
```

### ProdutoResponse (GET/POST/PUT)

```json
{
  "data": {
    "produtoId":     "integer",
    "produtoNome":   "string",
    "produtoValor":  "integer",
    "produtoCores":  ["string"],
    "produtoUrlMock":"string",
    "componentes":   [{ "componenteId": "integer", "componenteNome": "string", "componenteQuantidade": "integer" }]
  },
  "message": "string",
  "error":   "string"
}
```

### Envelope padrão de resposta

Todas as respostas seguem o padrão:
```json
{ "data": <objeto ou array>, "message": "string", "error": "string" }
```

---

## Tela Web — Rotas

| Rota (relativa à baseURL) | Tela |
|--------------------------|------|
| `` (vazio / raiz) | Tela de login |
| `produto` | Lista de produtos |
| `produto/novo` | Formulário de criação |
| `produto/editar/{id}` | Formulário de edição |
| `/lojinha-web/v2//produto/remover/{id}` | Remoção (URL absoluta — barra dupla) |

---
<!-- Fonte: bugs-conhecidos.md -->

# Lojinha — Bugs e Gotchas Conhecidos

## BUG #1 — HTTP 500 em vez de 401 para token inválido

| Campo | Detalhe |
|-------|---------|
| **ID** | BUG-001 |
| **Severidade** | Alta |
| **Status** | Aberto |
| **Detectado por** | NEXUS (RestAssured) |
| **Endpoint** | `POST /v2/produtos` |
| **Método de reprodução** | Enviar request com header `token: valor_invalido_qualquer` |
| **Comportamento atual** | HTTP **500** (Internal Server Error) |
| **Comportamento esperado** | HTTP **401** (Unauthorized) — conforme contrato OpenAPI |
| **Impacto** | Clientes que integram via API interpretam erro de autenticação como falha de servidor |

### Como reproduzir

```bash
curl -X POST http://165.227.93.41/lojinha/v2/produtos \
  -H "Content-Type: application/json" \
  -H "token: token_invalido" \
  -d '{"produtoNome":"Teste","produtoValor":100,"produtoCores":["preto"],"componentes":[{"componenteNome":"X","componenteQuantidade":1}]}'
# Retorna: 500 (deveria ser 401)
```

---

## BUG #2 — GET /v2/produtos sem paginação causa degradação de performance

| Campo | Detalhe |
|-------|---------|
| **ID** | BUG-002 |
| **Severidade** | Alta |
| **Status** | Aberto |
| **Detectado por** | FLUX (k6) |
| **Endpoint** | `GET /v2/produtos` |
| **Payload observado** | **41 KB** com apenas 1 usuário de teste |
| **Latência (1 usuário)** | **604ms** — viola SLA de 500ms com usuário único |
| **Causa raiz** | Dados acumulados de todas as sessões de teste; sem paginação implementada |
| **Risco projetado** | Com 10 usuários simultâneos → violação consistente do SLA de p95 < 500ms |

### Comportamento em comparação com SLA

| Cenário | Latência p95 | SLA | Status |
|---------|-------------|-----|--------|
| 1 usuário (smoke) | 604ms | 500ms | ❌ |
| 10 usuários (estimado) | >1000ms | 500ms | ❌ |

### Workaround atual

O endpoint aceita filtros por query string que reduzem o payload:
```
GET /v2/produtos?produtoNome=X
GET /v2/produtos?produtoCores=preto
```
Mas não existe paginação (`page` / `limit` / `offset`) — a correção exige mudança no backend.

---

## GOTCHA #1 — baseURL do Playwright precisa de subpath completo com barra final

**Contexto:** o app web fica em `/lojinha-web/v2/` (com barra final).

**Erro:** configurar `baseURL: 'http://165.227.93.41'` faz todas as navegações relativas apontarem para a raiz do servidor.

**Correto:**
```typescript
// playwright.config.ts
baseURL: 'http://165.227.93.41/lojinha-web/v2/'
//                                              ^ barra final obrigatória
```

---

## GOTCHA #2 — Remoção de produto usa barra dupla na URL

**Contexto:** a rota de remoção da Lojinha Web tem uma barra dupla (`//produto/remover/`).

**Sintoma:** navegar com `page.goto('produto/remover/123')` resulta em 404.

**Correto:**
```typescript
// ProdutoFormPage.ts — usando URL absoluta para evitar ambiguidade
await this.page.goto(`http://165.227.93.41/lojinha-web/v2//produto/remover/${id}`);
//                                                        ^^ barra dupla intencional
```

---

## GOTCHA #3 — Campo valor usa máscara jQuery (ProdutoFormPage)

**Contexto:** o campo `#produtovalor` tem máscara de formatação jQuery no frontend.

**Sintoma:** `fill('100')` em sequência pode concatenar ao valor existente, resultando em `"100100"` em vez de `"100"`.

**Correto:**
```typescript
await this.campoValor.clear();  // limpa primeiro
await this.campoValor.fill(valor);
```

---

## GOTCHA #4 — Seletores de label no Materialize CSS

**Contexto:** o app usa o framework Materialize CSS. Labels animados cobrem os inputs visualmente mas o DOM os associa diferente de HTML padrão.

**Sintoma:** `page.getByLabel('Usuário')` pode não encontrar o campo se o label não estiver corretamente associado ao `<input>` via `for`/`id`.

**Correto (testado e funcionando):**
```typescript
// LoginPage.ts
this.campoUsuario = page.getByLabel('Usuário');  // funciona — label usa for="usuario"
this.campoSenha   = page.getByLabel('Senha');     // funciona — label usa for="senha"

// ProdutoFormPage.ts — usa ID direto (mais robusto com Materialize)
this.campoNome  = page.locator('#produtonome');
this.campoValor = page.locator('#produtovalor');
this.campoCores = page.locator('#produtocores');
```

---

## GOTCHA #5 — Endpoint de login é /v2/login, não /v2/usuarios/login

**Contexto:** intuitivo seria `POST /v2/usuarios/login`, mas o contrato define `POST /v2/login`.

**Erro comum:**
```java
// ERRADO
post("/usuarios/login")

// CORRETO
post("/login")  // com RestAssured.basePath = "/v2", vira /v2/login
```

---

## GOTCHA #6 — JMeter smoke test com taxa de erro 4,44%

**Contexto:** execução do smoke test JMeter retornou p95 = 475ms (dentro do SLA) mas taxa de erro de **4,44%** (acima do threshold de 1%).

**Causa provável:** requests concorrentes ao endpoint `GET /v2/produtos` sobrecarregando a resposta sem paginação (BUG #2), causando timeouts ou erros intermitentes.

**Ação:** o BUG #2 deve ser corrigido antes de considerar os testes JMeter como baseline confiável.

---

## GOTCHA #7 — produtoValor é integer no contrato (não float)

**Contrato OpenAPI:**
```yaml
produtoValor:
  type: integer
  format: int32
```

**Regra de negócio:** valores aceitos são inteiros de **1 a 7000**. Valor 0 retorna HTTP 422. Valor acima de 7000 retorna HTTP 422.

**No JSON Schema de validação:**
```json
"produtoValor": { "type": "integer", "minimum": 1, "maximum": 7000 }
```

---
<!-- Fonte: decisoes.md -->

# Lojinha — Decisões Técnicas

## ARIA (Playwright TypeScript)

### D-A1 — Page Object Model como padrão de organização

**Decisão:** cada tela recebe uma classe Page Object dedicada em `pages/`.

**Por quê:** isolamento de seletores — quando o DOM muda, só o Page Object precisa ser atualizado, os testes permanecem estáveis. Padrão validado por Fernando Papito em projetos de consultoria.

**Page Objects criados:**
- `LoginPage` — tela de login (`/`)
- `ProdutoFormPage` — formulário de produto (`/produto/novo`, `/produto/editar/:id`)
- `ProdutoListaPage` — listagem de produtos (`/produto`)

---

### D-A2 — Seletores semânticos no LoginPage, IDs no ProdutoFormPage

**Decisão:** `LoginPage` usa `getByLabel()` e `getByRole()`; `ProdutoFormPage` usa `locator('#id')`.

**Por quê:** os campos de login têm labels bem associados no Materialize CSS e seletores semânticos são mais resilientes. O formulário de produto com máscara jQuery é mais estável com ID direto.

---

### D-A3 — fullyParallel: false no playwright.config.ts

**Decisão:** testes rodam sequencialmente (não em paralelo).

**Por quê:** os testes de produto compartilham estado no servidor (mesmo usuário `admin`). Paralelismo causaria conflitos de dados (produto criado por um teste sendo deletado por outro). Aceito para POC — em produção, cada worker deveria ter seu próprio usuário isolado.

---

### D-A4 — URL absoluta para remoção de produto

**Decisão:** `removerProduto()` usa URL absoluta ao invés de `page.goto()` relativo.

**Por quê:** a rota de remoção da app tem barra dupla (`//produto/remover/`), que `page.goto()` com path relativo resolve incorretamente. URL absoluta é explícita e não sofre normalização.

---

## NEXUS (RestAssured Java 17)

### D-N1 — Gradle como build tool (não Maven)

**Decisão:** projeto usa Gradle com `build.gradle` (Groovy DSL).

**Por quê:** mais conciso que Maven XML. Comando de execução: `./gradlew test`.

---

### D-N2 — baseURI sem /v2, basePath com /v2

**Decisão:**
```java
RestAssured.baseURI = "http://165.227.93.41/lojinha";  // sem /v2
RestAssured.basePath = "/v2";                           // /v2 aqui
```

**Por quê:** o endpoint de login é `/v2/login` e os de produto são `/v2/produtos`. Separar o basePath permite que `post("/login")` resulte em `/v2/login` corretamente. Se `/v2` ficasse no baseURI, seria difícil testar o endpoint `/v2/usuarios` que tem estrutura diferente.

---

### D-N3 — @TestMethodOrder(OrderAnnotation.class) em ProdutoApiTest

**Decisão:** testes de produto têm ordem definida via `@Order`.

**Por quê:** o teste cria um produto no `@Order(1)`, captura o `produtoId`, e usa esse ID nos testes de busca, edição e deleção subsequentes. Dependência de estado é intencional para simular fluxo real de CRUD.

---

### D-N4 — JSON Schema em classpath (não inline)

**Decisão:** o schema de validação fica em `src/test/resources/schemas/produto-schema.json`.

**Por quê:** reutilizável em múltiplos testes, versionável no git, editável sem recompilar Java. Carregado via `matchesJsonSchemaInClasspath("schemas/produto-schema.json")`.

---

### D-N5 — Variáveis de ambiente para credenciais, padrão embutido

**Decisão:** credenciais via env var com fallback hardcoded para `admin/admin`.

**Por quê:** funciona out-of-the-box para a Lojinha de teste (credenciais são públicas), mas permite sobrescrever em pipelines CI com credenciais de outros ambientes sem alterar código.

---

## FLUX (k6 + JMeter)

### D-F1 — config.js centraliza SLAs e credenciais para k6

**Decisão:** `config.js` é o único lugar onde SLAs e BASE_URL são definidos.

**Por quê:** mudança de ambiente ou threshold requer edição em um único arquivo. Padrão de Vinícius Pessoni: "percentis, nunca médias — p95 e p99 são os números que importam".

---

### D-F2 — SLAs definidos por endpoint (não só global)

**Decisão:**
```javascript
'http_req_duration{endpoint:login}':    ['p(95)<300'],  // mais restrito
'http_req_duration{endpoint:produtos}': ['p(95)<500'],
```

**Por quê:** login é gargalo de sessão — se demorar mais de 300ms, todas as operações subsequentes ficam prejudicadas. Endpoints de dado têm tolerância maior (500ms).

---

### D-F3 — Smoke test antes de qualquer load test

**Decisão:** sempre executar `smoke.js` (1 VU, 1 min) antes de `stress.js` ou `login-load.js`.

**Por quê:** confirma que a API está saudável antes de aplicar carga. Falha no smoke = não executar carga (evita mascarar problemas com dados de carga ruidosos).

---

### D-F4 — Métricas customizadas por etapa do fluxo

**Decisão:** `smoke.js` cria Trends separados: `duracao_login`, `duracao_criar`, `duracao_listar`, `duracao_buscar`, `duracao_deletar`.

**Por quê:** permite identificar qual etapa específica do fluxo está lenta, não apenas "alguma coisa está devagar".

---

## Geral

### D-G1 — CI-ready por design (tudo via linha de comando)

**Decisão:** nenhum projeto depende de IDE, plugin ou configuração manual para executar.

| Projeto | Comando |
|---------|---------|
| Playwright | `npx playwright test` |
| RestAssured | `./gradlew test` |
| k6 smoke | `k6 run lojinha-performance/k6/smoke.js` |
| JMeter smoke | `jmeter -n -t lojinha-performance/jmeter/lojinha-smoke.jmx -l results.jtl` |

---

### D-G2 — Token via header `token` (não Bearer)

**Decisão:** todas as chamadas autenticadas usam o header `token: <valor>`.

**Por quê:** esse é o contrato da Lojinha API — não usa padrão `Authorization: Bearer`. Desviar disso causa 401 ou 500 silencioso.
