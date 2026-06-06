*** Settings ***
Library    AppiumLibrary
Library    OperatingSystem

*** Variables ***
${APPIUM_URL}     http://localhost:4723/wd/hub
${PLATFORM}       Android
${APP}            /Users/robsonrocha/Downloads/qa-agents/mobile/android/apk/twp.apk
${DEVICE_NAME}    902a612
${PLATFORM_VER}   13
${TIMEOUT}        15s
${APP_ID}         io.qaninja.android.twp

*** Keywords ***
Abrir Aplicativo
    Run    adb -s ${DEVICE_NAME} shell pm clear ${APP_ID}
    Open Application    ${APPIUM_URL}
    ...    platformName=${PLATFORM}
    ...    deviceName=${DEVICE_NAME}
    ...    platformVersion=${PLATFORM_VER}
    ...    appPackage=${APP_ID}
    ...    appActivity=.components.base.SplashActivity
    ...    automationName=UiAutomator2
    ...    noReset=${TRUE}
    Set Appium Timeout    ${TIMEOUT}

Fechar Aplicativo
    Close Application
