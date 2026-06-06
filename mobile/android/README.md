# Android Test Environment — TWP

## Pré-requisitos

- Android Studio + Android SDK instalado
- `ANDROID_HOME` configurado no PATH
- Java 11+
- Node.js 18+ (para Appium)
- Python 3.10+

## Setup do Device

```bash
# Listar devices disponíveis
adb devices

# Instalar o APK
adb install apk/twp.apk
```

## Maestro

```bash
# Instalar Maestro
curl -Ls "https://get.maestro.mobile.dev" | bash

# Rodar um flow
maestro test maestro/flows/login.yaml

# Rodar todos os flows
maestro test maestro/flows/
```

## Robot Framework + Appium

```bash
# Instalar dependências Python
pip install -r robot/requirements.txt

# Iniciar Appium server (terminal separado)
appium

# Rodar os testes
robot --outputdir results robot/tests/

# Rodar apenas login
robot --outputdir results robot/tests/login_tests.robot
```

## Estrutura

```
android/
  apk/            ← APK do app
  maestro/
    flows/        ← Flows Maestro (.yaml)
    config.yaml   ← Config global
  robot/
    resources/    ← Keywords e variáveis compartilhadas
    tests/        ← Suítes de teste (.robot)
    requirements.txt
```
