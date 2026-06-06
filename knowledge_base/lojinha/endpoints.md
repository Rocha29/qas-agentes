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
