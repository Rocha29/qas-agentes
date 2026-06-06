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
