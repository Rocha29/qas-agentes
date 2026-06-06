# iOS Tests — KAUE-MOBILE

Testes de automação iOS usando **Maestro** com simulador e dispositivo real via Maestro Cloud.

## Estrutura

```
mobile/ios/
├── maestro/
│   ├── config.yaml                    # Agrupa todos os flows
│   └── flows/
│       └── safari_google_search.yaml  # Safari → Google → pesquisa "nekalst"
└── README.md
```

## Pré-requisitos

- macOS com Xcode instalado
- Simulador iOS configurado (`xcrun simctl list devices`)
- Maestro CLI: `curl -fsSL "https://get.maestro.mobile.dev" | bash`

## Rodar localmente

```bash
# Inicia o simulador (substitua pelo UDID do seu dispositivo)
xcrun simctl boot <UDID>
open -a Simulator

# Executa o flow
maestro test mobile/ios/maestro/flows/safari_google_search.yaml

# Executa todos os flows
maestro test mobile/ios/maestro/config.yaml
```

## Executar no CI

O workflow `.github/workflows/ios-tests.yml` roda automaticamente em pushes que alteram `mobile/ios/**`.

Pode também ser disparado manualmente em **Actions → iOS Tests → Run workflow** com parâmetros:
- `ios_version`: versão do iOS (padrão: `17`)
- `device`: nome do simulador (padrão: `iPhone 15`)

## Maestro Cloud (dispositivo real)

Configure o secret `MAESTRO_CLOUD_API_KEY` no repositório e a variável `USE_MAESTRO_CLOUD=true`.
O job `ios-cloud` só roda via `workflow_dispatch`.
