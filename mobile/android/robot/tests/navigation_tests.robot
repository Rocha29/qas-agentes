*** Settings ***
Resource    ../resources/login_keywords.resource
Suite Setup    Abrir Aplicativo
Suite Teardown    Fechar Aplicativo

*** Test Cases ***
Navegar Para Home Após Login
    Preencher E-mail    usuario@teste.com
    Preencher Senha     senha123
    Clicar em Entrar
    Login Deve Ser Bem-sucedido
    Click Element    id=nav_home
    Element Should Be Visible    id=home_screen

Navegar Para Perfil
    Click Element    id=nav_profile
    Element Should Be Visible    id=profile_screen
