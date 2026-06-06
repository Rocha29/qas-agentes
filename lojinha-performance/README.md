# lojinha-performance — Testes de Performance

Suíte de performance para a Lojinha API com dois toolings: **k6** (scripting JavaScript) e **JMeter** (planos XML).

## Pré-requisitos

- k6: `brew install k6` (macOS) ou https://k6.io/docs/getting-started/installation/
- JMeter 5.6+: https://jmeter.apache.org/download_jmeter.cgi
- Lojinha API rodando em `http://165.227.93.41`

## k6

```bash
cd k6

k6 run smoke.js          # Smoke — 1 VU, 1 min
k6 run login-load.js     # Load — login endpoint
k6 run produtos-load.js  # Load — endpoint de produtos
k6 run stress.js         # Stress — rampa agressiva
```

### SLAs monitorados

| Métrica | Threshold |
|---------|-----------|
| p95 response time | < 500ms |
| Error rate | < 1% |
| p99 response time | < 1000ms |

## JMeter

```bash
cd jmeter

# Via script (requer JMETER_HOME no PATH)
chmod +x run.sh && ./run.sh

# Manualmente
jmeter -n -t lojinha-smoke.jmx -l results/smoke.jtl -e -o results/report
```

## Resultados da POC

- k6 smoke: passou dentro dos SLAs
- JMeter stress: alerta de degradação de p95 sob carga elevada — bug identificado para investigação
