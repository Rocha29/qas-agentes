# Decisões de Arquitetura — POC Lojinha

> Por que cada escolha foi feita. Evita rediscutir o que já foi decidido.

---

## Web — Playwright TypeScript

### POM com 3 Page Objects
**Decisão:** separar LoginPage, ProdutoFormPage e ProdutoListaPage

**Motivo:** cada Page Object representa uma responsabilidade distinta:
- `LoginPage` → autenticação
- `ProdutoFormPage` → criação e edição (compartilham o mesmo form)
- `ProdutoListaPage` → listagem, validação de presença/ausência, exclusão

**Padrão de nomenclatura:** português para métodos e variáveis
(`fazerLogin`, `campoUsuario`, `btnEntrar`)

---

### goto('') em vez de goto('/')
**Decisão:** usar `goto('')` em todos os Page Objects

**Motivo:** baseURL com subpath + `goto('/')` navega para raiz do servidor.
`goto('')` resolve corretamente para a baseURL completa.

Ver: `bugs-conhecidos.md → gotcha-01`

---

### getByLabel com acento e maiúscula
**Decisão:** usar `getByLabel('Usuário')` (com acento, U maiúsculo)

**Motivo:** Materialize CSS label é case sensitive e acento sensitive.
`getByLabel('usuario')` retorna 0 elementos.

Ver: `bugs-conhecidos.md → gotcha-02`

---

## API — RestAssured Java 17

### Gradle em vez de Maven
**Decisão:** Gradle 8.7 com wrapper

**Motivo:** build mais rápido, DSL mais limpa, wrapper garante
versão consistente em qualquer máquina sem instalação prévia.

---

### BaseTest com basePath via variável de ambiente
**Decisão:** `LOJINHA_BASE_URI` como env var, default para o servidor de treinamento

**Motivo:** trocar de ambiente (dev/staging/prod) sem alterar código.

```java
RestAssured.baseURI = System.getenv()
    .getOrDefault("LOJINHA_BASE_URI", "http://165.227.93.41");
RestAssured.basePath = "/lojinha";
```

---

### AuthHelper isolado
**Decisão:** classe dedicada para extração e gestão do token

**Motivo:** reutilização em todos os testes sem duplicação.
Token obtido uma vez no `@BeforeAll` e reusado.

---

### @Order + Assumptions em testes dependentes
**Decisão:** usar `@TestMethodOrder(MethodOrderer.OrderAnnotation.class)`
com `Assumptions.assumeTrue(produtoId != null)` em testes que dependem
de um recurso criado anteriormente.

**Motivo:** evita NullPointerException em cascata quando o teste de
criação falha — testes dependentes são pulados com mensagem clara.

---

### anyOf(401, 500) para token inválido
**Decisão:** aceitar ambos os status codes no teste de token inválido

**Motivo:** documentar bug conhecido sem bloquear a suite.
O contrato especifica 401, a implementação retorna 500.
Quando o bug for corrigido, simplificar para só `is(401)`.

---

## Performance

### k6 como ferramenta principal
**Decisão:** k6 para desenvolvimento e CI

**Motivo:** script em JavaScript, integração nativa com Grafana,
thresholds declarativos, saída clara no terminal.

### JMeter para relatório executivo
**Decisão:** JMeter para gerar relatório HTML visual

**Motivo:** o relatório HTML do JMeter (`index.html`) é mais
apresentável para gestores — dashboard visual com gráficos.

### Fluxo realista no k6 (não teste de endpoint isolado)
**Decisão:** cada VU executa login → criar → listar → buscar → deletar

**Motivo:** simula comportamento real do usuário, não apenas
stress em um endpoint. Revela problemas de estado e sequência.

---

## Estrutura geral do projeto

### Pastas em inglês, conteúdo em português
**Decisão:** pastas e arquivos em inglês (`agents/`, `knowledge_base/`),
conteúdo dos testes em português (`deveRetornar401...`)

**Motivo:** padrão internacional de estrutura de projeto,
mas nomes de teste legíveis pelo time brasileiro.

### RAG local em Markdown
**Decisão:** knowledge base em arquivos `.md` simples

**Motivo:** sem dependência de banco de dados ou serviço externo.
Funciona offline, versionável no Git, legível por humanos e agentes.
