# lojinha-api-tests — Testes de API com RestAssured

Suíte de testes de contrato e integração de API para a Lojinha, implementada com **RestAssured + Java 17 + JUnit 5 + Gradle**, com contrato OpenAPI validado.

## Pré-requisitos

- Java JDK 17+
- Lojinha API rodando em `http://165.227.93.41`

## Execução

```bash
# Rodar todos os testes
./gradlew test

# Relatório HTML
open build/reports/tests/test/index.html
```

## Estrutura

```
lojinha-api-tests/
├── src/test/java/       # Testes JUnit 5 com RestAssured
├── src/test/resources/  # Dados de teste e configurações
├── lojinha-v2.yml       # Contrato OpenAPI da API
├── build.gradle
└── gradlew
```

## Resultados da POC

17/17 testes passando — cobertura de autenticação, CRUD de produtos e validação de contrato OpenAPI.
