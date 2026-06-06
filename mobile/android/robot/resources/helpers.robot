*** Settings ***
Resource    base.robot

*** Keywords ***
Go To Login Forms
    Wait Until Page Contains Element    io.qaninja.android.twp:id/drawerLayout    timeout=10s
    Swipe    30    600    700    600    500
    Wait Until Page Contains Element    io.qaninja.android.twp:id/rvNavigation    timeout=5s
    Click Text    FORMS
    Click Text    LOGIN
    Wait Until Page Contains Element    io.qaninja.android.twp:id/etEmail    timeout=10s
