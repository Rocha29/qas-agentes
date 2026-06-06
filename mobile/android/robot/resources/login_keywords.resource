*** Settings ***
Resource    common.resource

*** Variables ***
${BTN_COMECAR}          id=io.qaninja.android.twp:id/mi_button_cta
${LBL_QA_NINJA}         xpath=//android.widget.TextView[@text='QA Ninja']
${LBL_AVENGERS}         xpath=//android.widget.TextView[@text='AVENGERS']
${ID_TOOLBAR_TITLE}     id=io.qaninja.android.twp:id/toolbarTitle
${ID_DRAWER_LAYOUT}     id=io.qaninja.android.twp:id/drawerLayout

*** Keywords ***
Tela De Onboarding Deve Estar Visível
    Wait Until Element Is Visible    ${LBL_QA_NINJA}    timeout=${TIMEOUT}
    Element Should Be Visible        ${BTN_COMECAR}

Passar Pelo Onboarding
    Tela De Onboarding Deve Estar Visível
    Click Text    COMEÇAR

Home Deve Estar Visível
    Wait Until Page Does Not Contain Element    ${BTN_COMECAR}    timeout=${TIMEOUT}
