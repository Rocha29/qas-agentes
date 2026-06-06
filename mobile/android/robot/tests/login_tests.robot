*** Settings ***
Resource        ../resources/login_keywords.resource
Suite Setup     Abrir Aplicativo
Suite Teardown  Fechar Aplicativo

*** Test Cases ***
Onboarding Exibe Tela De Boas-vindas
    Tela De Onboarding Deve Estar Visível

Tap Em Começar Navega Para Home
    Wait Until Element Is Visible    ${LBL_QA_NINJA}    timeout=${TIMEOUT}
    Click Text    COMEÇAR
    Wait Until Page Does Not Contain Element    ${BTN_COMECAR}    timeout=${TIMEOUT}
