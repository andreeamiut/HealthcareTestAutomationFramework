*** Settings ***
Documentation    Main Robot Framework configuration file for Healthcare Test Automation Framework
Library          Collections
Library          DateTime
Library          String
Library          OperatingSystem
Resource         ${CURDIR}/config/environments.robot
Resource         ${CURDIR}/keywords/common_keywords.robot
Resource         ${CURDIR}/keywords/patient_keywords.robot
Resource         ${CURDIR}/keywords/appointment_keywords.robot
Resource         ${CURDIR}/keywords/authentication_keywords.robot

*** Variables ***
# Global Test Settings
${TIMEOUT}                     30s
${RETRY_COUNT}                 3
${SCREENSHOT_ON_FAILURE}       True
${HEADLESS_MODE}              False
${BROWSER_TYPE}               chromium

# Healthcare Domain Constants
${PATIENT_ID_PREFIX}          PAT
${APPOINTMENT_ID_PREFIX}      APT
${PROVIDER_ID_PREFIX}         PRV

# Test Data Paths
${TEST_DATA_DIR}              ${CURDIR}/data/test_data
${SQL_SCRIPTS_DIR}            ${CURDIR}/data/sql_scripts
${RESULTS_DIR}                ${CURDIR}/results

# URLs will be loaded from environment-specific files
${BASE_URL}                   ${EMPTY}
${API_BASE_URL}               ${EMPTY}

*** Keywords ***
Test Setup
    [Documentation]    Common setup for all tests
    Log    Starting test: ${TEST NAME}
    Set Screenshot Directory    ${RESULTS_DIR}/screenshots
    Set Global Variable    ${START_TIME}    ${CURRENT_DATETIME}

Test Teardown
    [Documentation]    Common teardown for all tests
    Run Keyword If    '${TEST STATUS}' == 'FAIL'    Capture Page Screenshot
    Log    Test completed: ${TEST NAME} - Status: ${TEST STATUS}
    Close All Browsers

Suite Setup
    [Documentation]    Common setup for test suites
    Log    Starting test suite: ${SUITE NAME}
    Create Directory    ${RESULTS_DIR}/screenshots
    Create Directory    ${RESULTS_DIR}/logs
    ${current_datetime}=    Get Current Date    result_format=%Y-%m-%d %H:%M:%S
    Set Global Variable    ${CURRENT_DATETIME}    ${current_datetime}

Suite Teardown
    [Documentation]    Common teardown for test suites
    Log    Test suite completed: ${SUITE NAME}
    Close All Browsers