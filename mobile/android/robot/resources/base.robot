*** Settings ***
Library     AppiumLibrary
Library     DateTime

*** Keywords ***
Open Session
    Set Appium Timeout  10
    Open Application    http://localhost:4723/wd/hub
    ...                 automationName=UiAutomator2
    ...                 platformName=Android
    ...                 deviceName=902a612
    ...                 app=${EXECDIR}/app/twp.apk
    Get Started

Close Session
    ${date}=            Get Current Date        exclude_millis=yes
    Capture Page Screenshot    ${TEST NAME} ${date}.png
    Close Application

Get Started
    Wait Until Page Contains Element    //*[@text='COMEÇAR']    timeout=10s
    Click Text    COMEÇAR
    ${on_home}=    Run Keyword And Return Status
    ...    Wait Until Page Contains Element    io.qaninja.android.twp:id/drawerLayout    timeout=5s
    Run Keyword If    not ${on_home}    Click Text    COMEÇAR
    Wait Until Page Contains Element    io.qaninja.android.twp:id/drawerLayout    timeout=10s
