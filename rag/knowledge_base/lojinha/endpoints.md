# Endpoints da API — Lojinha v2

> Mapeado via contrato OpenAPI: http://165.227.93.41/lojinha/lojinha-v2.yml
> Host: 165.227.93.41 | BasePath: /lojinha

---

## Autenticação

### POST /v2/login
```json
// Request
{
  "usuarioLogin": "admin",
  "usuarioSenha": "admin"
}

// Response 200
{
  "token": "eyJ...",
  "userId": 1
}
```

### POST /v2/usuarios
Cadastro de novo usuário.

### DELETE /v2/dados
Limpeza de dados do usuário.

---

## Produtos

### POST /v2/produtos
```json
// Request — header obrigatório: token: {token}
{
  "produtoNome": "Nome do Produto",
  "produtoValor": 100,
  "produtosCores": ["Azul", "Verde"],
  "produtoImagem": "imagem.jpg"
}

// Response 201
{
  "produtoId": 123,
  "produtoNome": "Nome do Produto",
  "produtoValor": 100
}

// Validações (422):
// - produtoValor = 0 → inválido
// - produtoValor > 7000 → inválido
// - produtoNome vazio → inválido
```

### GET /v2/produtos
```
// Response 200 — lista todos os produtos do usuário
// ⚠️ BUG #2: sem paginação, payload cresce indefinidamente
```

### GET /v2/produtos/{produtoId}
```json
// Response 200
{
  "produtoId": 123,
  "produtoNome": "...",
  "produtoValor": 100,
  "componentes": []
}
// Response 404 — produto não encontrado
```

### PUT /v2/produtos/{produtoId}
```json
// Request — mesmo body do POST
// Response 200 — produto atualizado
```

### DELETE /v2/produtos/{produtoId}
```
// Response 204 — sem body
```

---

## Componentes

### POST /v2/produtos/{produtoId}/componentes
```json
// Request
{
  "componenteNome": "Nome",
  "componenteQuantidade": 5
}
// Response 201
```

### GET /v2/produtos/{produtoId}/componentes/{componenteId}
```
// Response 200
```

### PUT /v2/produtos/{produtoId}/componentes/{componenteId}
```
// Response 200
```

### DELETE /v2/produtos/{produtoId}/componentes/{componenteId}
```
// Response 204
```

---

## Status Codes de Referência

| Code | Significado | Quando ocorre |
|------|-------------|---------------|
| 200 | OK | GET, PUT bem-sucedidos |
| 201 | Created | POST bem-sucedido |
| 204 | No Content | DELETE bem-sucedido |
| 401 | Unauthorized | Token ausente ou inválido |
| 404 | Not Found | Recurso não existe |
| 422 | Unprocessable | Validação de negócio falhou |
| 500 | Server Error | BUG #1 — token mal-formado |
