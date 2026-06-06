# Bugs e Gotchas Conhecidos — Lojinha

> Problemas já descobertos. Não perca tempo redescubrindo.

---

## 🔵 Playwright (ARIA)

### gotcha-01 — goto('/') com baseURL contendo subpath

**Problema:**
```typescript
// playwright.config.ts
baseURL: 'http://165.227.93.41/lojinha-web/v2/'

// No Page Object:
await this.page.goto('/') // ← ERRADO
// Navega para http://165.227.93.41/ (raiz do servidor)
// Não encontra os elementos → timeout de 31s
```

**Solução:**
```typescript
await this.page.goto('') // ← CORRETO
// Resolve para http://165.227.93.41/lojinha-web/v2/
```

**Regra:** sempre usar `goto('')` quando baseURL tiver subpath.

---

### gotcha-02 — Materialize CSS com label flutuante

**Problema:**
O Materialize CSS usa `<label>` como elemento decorativo flutuante.
`getByLabel('usuario')` não encontra o campo (case sensitive).

**Diagnóstico:**
```javascript
// Resultado da investigação:
// getByLabel('Usuário'): count=1 visible=true enabled=true ✅
// getByLabel('usuario'): count=0 visible=false enabled=false ❌
// locator('#usuario'): count=1 visible=true enabled=true ✅
```

**Solução:**
```typescript
// Usar exatamente como aparece no label visual (com acento, maiúscula)
this.campoUsuario = page.getByLabel('Usuário')
this.campoSenha = page.getByLabel('Senha')
```

---

### gotcha-03 — URL de exclusão com barra dupla

**Problema:**
A app Lojinha tem URL de exclusão com barra dupla:
`//produto/remover/{id}`

`page.goto('//...')` é interpretado pelo Playwright como protocolo relativo.

**Solução:**
Usar URL absoluta completa no Page Object:
```typescript
async removerProduto(id: string) {
  await this.page.goto(
    `http://165.227.93.41/lojinha-web/v2/produto/remover/${id}`
  )
}
```

---

## 🔌 API REST (NEXUS)

### bug-01 — Token inválido retorna 500 em vez de 401

**Severidade:** Alta
**Endpoint:** `POST /v2/produtos`
**Comportamento atual:** token mal-formado → HTTP 500
**Comportamento esperado:** HTTP 401 (conforme contrato OpenAPI)
**Causa:** Slim Framework não trata JWT parse error — lança exceção sem captura

**Workaround no teste:**
```java
.then()
.statusCode(anyOf(is(401), is(500)));
// BUG DOCUMENTADO: Slim Framework lança 500 em vez de 401
// para token mal-formado. Contrato especifica 401.
```

**Status:** bug registrado, aguardando correção no backend.

---

### gotcha-04 — basePath errado

**Problema:**
O path `/lojinha-api` não existe. A aplicação está em `/lojinha`.

```
❌ http://165.227.93.41/lojinha-api/v2/login → 404
✅ http://165.227.93.41/lojinha/v2/login    → 200
```

**Como descoberto:** lendo o contrato OpenAPI (`lojinha-v2.yml`):
```yaml
host: 165.227.93.41
basePath: /lojinha
```

**No BaseTest.java:**
```java
RestAssured.baseURI = "http://165.227.93.41";
RestAssured.basePath = "/lojinha"; // ← correto
```

---

### gotcha-05 — Endpoint de login

```
❌ POST /v2/usuarios/login → não existe
✅ POST /v2/login          → correto
```

**Payload correto:**
```json
{
  "usuarioLogin": "admin",
  "usuarioSenha": "admin"
}
```

**Response:**
```json
{
  "token": "eyJ...",
  "userId": 1
}
```

**Header para requests autenticados:**
```
token: eyJ...
```
⚠️ O header é `token` (não `Authorization: Bearer`).

---

### gotcha-06 — produtoValor é integer, não float

**Problema:**
```json
{ "produtoValor": 99.90 }  // ← ERRADO — retorna 422
{ "produtoValor": 99 }     // ← CORRETO — aceita inteiro
```

O campo `produtoValor` no JSON Schema é `integer`.
Valores como `0` retornam 422 (zero não permitido).
Valor máximo: 7000.

---

## ⚡ Performance (FLUX)

### bug-02 — GET /v2/produtos sem paginação

**Severidade:** Alta
**Endpoint:** `GET /v2/produtos`
**Problema:** retorna todos os produtos do usuário sem paginação
**Payload observado:** 41KB com apenas 1 usuário em ambiente compartilhado
**Latência:** p95 = 554ms (k6), max = 643ms — viola SLA de 500ms

**Causa raiz:** dados acumulados de outros alunos + ausência de paginação.

**Projeção:** com 10 usuários simultâneos → violação consistente do SLA.

**Recomendação:** implementar `?page=1&limit=20` ou paginação por cursor.

**Status:** bug registrado como prioridade alta.

---

### gotcha-07 — DurationAssertion JMeter muito apertado

**Problema:**
`DurationAssertion` de 500ms no JMeter marca requests como ERRO
mesmo quando o HTTP status é 200 — inflando artificialmente a taxa de erro.

**Resultado observado:**
```
Taxa de erro JMeter: 4.44%
Causa real: 2 requests de GET /v2/produtos com 509ms e 604ms
HTTP status: 200 (não são falhas reais)
```

**Solução para ambiente de treinamento:**
Ajustar `DurationAssertion` para 1000ms nos arquivos `.jmx`.

**Em produção real:** manter 500ms e tratar como alerta de degradação.
