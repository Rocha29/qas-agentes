# [HIST-XXX] — [Título da História Técnica]

**Tipo:** técnica
**Sprint:** [número]
**Criado por:** Tech Lead
**Data:** [YYYY-MM-DD]

---

## Descrição Técnica

[Descreva o que precisa ser construído — ex: "Criar BFF para o módulo de produtos, consumido pelo front web e app mobile Android/iOS"]

---

## Especificação da API / BFF

**Base URL:** `[ex: /api/v1/]`

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/produtos` | Lista produtos paginada |
| POST | `/produtos` | Cria novo produto |
| PUT | `/produtos/{id}` | Atualiza produto |
| DELETE | `/produtos/{id}` | Remove produto |

### Exemplo de contrato (request/response)

```json
// POST /produtos
// Request
{
  "nome": "string",
  "preco": "number",
  "categoriaId": "string"
}

// Response 201
{
  "id": "uuid",
  "nome": "string",
  "preco": "number",
  "criadoEm": "ISO8601"
}
```

---

## Consumidores do BFF

<!-- Marque todos que se aplicam -->

- [ ] Front Web (React / Vue / Angular)
- [ ] App Mobile Android
- [ ] App Mobile iOS
- [ ] WebView dentro do app
- [ ] Outro serviço interno

---

## SLA e performance esperada

| Endpoint | p95 esperado | p99 máximo | Volume estimado |
|----------|-------------|-----------|----------------|
| GET /produtos | < [Xms] | < [Xms] | [N] req/min |
| POST /produtos | < [Xms] | < [Xms] | [N] req/min |

---

## Autenticação / Autorização

- [ ] JWT Bearer Token
- [ ] API Key
- [ ] OAuth 2.0
- [ ] Pública (sem auth)
- Roles necessárias: [ex: ADMIN, USER]

---

## Risco estimado

- [ ] Alto — integração com serviço externo, pagamento, dados sensíveis
- [ ] Médio — nova feature core
- [ ] Baixo — endpoint de apoio, listagem interna

---

## Documentação de referência

- Swagger/OpenAPI: [link ou arquivo .yml]
- Diagrama de sequência: [link]
- Repositório: [link]

---

## Notas para os agentes

<!-- O Tech Lead pode deixar observações específicas aqui -->

-
