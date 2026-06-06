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
