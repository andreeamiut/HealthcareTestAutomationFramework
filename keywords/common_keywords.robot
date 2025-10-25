*** Settings ***
Documentation    Common keywords shared across all healthcare test suites
Library          Browser
Library          Collections
Library          DateTime  
Library          String
Library          OperatingSystem
Library          ../libraries/PlaywrightHealthcareLibrary.py
Library          ../libraries/DatabaseHealthcareLibrary.py
Library          ../libraries/APIHealthcareLibrary.py

*** Variables ***
${WAIT_TIMEOUT}              30s
${SHORT_WAIT}               5s
${LOADING_INDICATOR}        css:.loading-spinner
${ERROR_MESSAGE}            css:.error-message
${SUCCESS_MESSAGE}          css:.success-message

*** Keywords ***
Initialize Test Environment
    [Documentation]    Sets up the test environment with proper configuration
    [Arguments]    ${environment}=dev
    
    Load Environment Configuration    ${environment}
    Set Global Variable    ${TEST_START_TIME}    ${CURRENT_DATETIME}
    Create Directory    ${RESULTS_DIR}/screenshots
    Create Directory    ${RESULTS_DIR}/logs
    Log    Test environment initialized: ${environment}

Setup Browser For Healthcare Tests
    [Documentation]    Opens browser with healthcare-specific settings
    [Arguments]    ${url}=${BASE_URL}    ${browser}=${BROWSER_TYPE}    ${headless}=${HEADLESS_MODE}
    
    Open Healthcare Application    ${url}    ${browser}    ${headless}
    Wait For Page Load    timeout=${WAIT_TIMEOUT}
    Validate HIPAA Compliance Elements
    Log    Browser setup completed for healthcare application

Wait For Element To Be Visible
    [Documentation]    Waits for element to become visible with timeout
    [Arguments]    ${locator}    ${timeout}=${WAIT_TIMEOUT}
    
    Wait For Elements State    ${locator}    visible    timeout=${timeout}

Wait For Element To Be Hidden
    [Documentation]    Waits for element to be hidden
    [Arguments]    ${locator}    ${timeout}=${WAIT_TIMEOUT}
    
    Wait For Elements State    ${locator}    hidden    timeout=${timeout}

Wait For Page Load
    [Documentation]    Waits for page to fully load
    [Arguments]    ${timeout}=${WAIT_TIMEOUT}
    
    Wait For Load State    networkidle    timeout=${timeout}
    Wait For Element To Be Hidden    ${LOADING_INDICATOR}    timeout=${SHORT_WAIT}

Click Element Safely
    [Documentation]    Clicks element with retry mechanism and validation
    [Arguments]    ${locator}    ${timeout}=${WAIT_TIMEOUT}
    
    Wait For Element To Be Visible    ${locator}    ${timeout}
    Wait For Elements State    ${locator}    enabled    timeout=${timeout}
    Click    ${locator}
    Sleep    0.5s    # Brief pause for action to register

Input Text Safely
    [Documentation]    Inputs text with validation and clearing
    [Arguments]    ${locator}    ${text}    ${timeout}=${WAIT_TIMEOUT}
    
    Wait For Element To Be Visible    ${locator}    ${timeout}
    Clear Text    ${locator}
    Type Text    ${locator}    ${text}
    
    # Validate text was entered correctly
    ${entered_value}=    Get Property    ${locator}    value
    Should Be Equal    ${entered_value}    ${text}    Text input validation failed

Select From Dropdown
    [Documentation]    Selects option from dropdown with validation
    [Arguments]    ${dropdown_locator}    ${option_text}    ${timeout}=${WAIT_TIMEOUT}
    
    Wait For Element To Be Visible    ${dropdown_locator}    ${timeout}
    Click    ${dropdown_locator}
    
    ${option_locator}=    Set Variable    text=${option_text}
    Wait For Element To Be Visible    ${option_locator}    ${SHORT_WAIT}
    Click    ${option_locator}
    
    # Validate selection
    ${selected_text}=    Get Text    ${dropdown_locator}
    Should Contain    ${selected_text}    ${option_text}

Verify Error Message Displayed
    [Documentation]    Verifies that an error message is displayed
    [Arguments]    ${expected_message}
    
    Wait For Element To Be Visible    ${ERROR_MESSAGE}    ${SHORT_WAIT}
    ${actual_message}=    Get Text    ${ERROR_MESSAGE}
    Should Contain    ${actual_message}    ${expected_message}
    Log    Error message verified: ${expected_message}

Verify Success Message Displayed
    [Documentation]    Verifies that a success message is displayed
    [Arguments]    ${expected_message}
    
    Wait For Element To Be Visible    ${SUCCESS_MESSAGE}    ${SHORT_WAIT}
    ${actual_message}=    Get Text    ${SUCCESS_MESSAGE}
    Should Contain    ${actual_message}    ${expected_message}
    Log    Success message verified: ${expected_message}

Verify Page Title
    [Documentation]    Verifies the current page title
    [Arguments]    ${expected_title}
    
    ${actual_title}=    Get Title
    Should Be Equal    ${actual_title}    ${expected_title}
    Log    Page title verified: ${expected_title}

Capture Screenshot With Timestamp
    [Documentation]    Captures screenshot with timestamp for debugging
    [Arguments]    ${test_name}=default
    
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
    ${screenshot_name}=    Set Variable    ${test_name}_${timestamp}
    Take Screenshot    filename=${RESULTS_DIR}/screenshots/${screenshot_name}
    Log    Screenshot captured: ${screenshot_name}

Navigate To Section
    [Documentation]    Navigates to a specific section using menu
    [Arguments]    ${section_name}
    
    ${menu_item}=    Set Variable    text=${section_name}
    Click Element Safely    ${menu_item}
    Wait For Page Load
    Log    Navigated to section: ${section_name}

Verify Data Grid Contains
    [Documentation]    Verifies that data grid contains specific data
    [Arguments]    ${grid_locator}    ${expected_data}
    
    Wait For Element To Be Visible    ${grid_locator}    ${WAIT_TIMEOUT}
    ${grid_text}=    Get Text    ${grid_locator}
    Should Contain    ${grid_text}    ${expected_data}
    Log    Data grid contains expected data: ${expected_data}

Logout Safely
    [Documentation]    Performs safe logout with session cleanup
    
    ${logout_button}=    Set Variable    css:[data-testid="logout-button"]
    TRY
        Click Element Safely    ${logout_button}
        Wait For Element To Be Visible    css:input[name="username"]    ${WAIT_TIMEOUT}
        Log    Logout completed successfully
    EXCEPT
        Log    Logout button not found, clearing session manually    level=WARN
        Go To    ${BASE_URL}/logout
    END

Handle Unexpected Modal
    [Documentation]    Handles unexpected modal dialogs
    
    TRY
        ${modal_present}=    Get Element Count    css:.modal.show
        IF    ${modal_present} > 0
            Log    Unexpected modal detected, attempting to close    level=WARN
            ${close_button}=    Set Variable    css:.modal .btn-close, css:.modal .close
            Click    ${close_button}
            Wait For Element To Be Hidden    css:.modal.show    ${SHORT_WAIT}
        END
    EXCEPT
        Log    No modal handling needed    level=DEBUG
    END

Verify HIPAA Audit Trail
    [Documentation]    Verifies HIPAA audit trail for database operations
    [Arguments]    ${patient_id}    ${action}    ${user_id}
    
    Connect To Healthcare Database    postgresql    ${DB_HOST}    ${DB_PORT}    ${DB_NAME}    ${DB_USER}    ${DB_PASSWORD}
    ${audit_verified}=    Verify HIPAA Audit Trail    ${patient_id}    ${action}    ${user_id}
    Should Be True    ${audit_verified}    HIPAA audit trail verification failed
    Disconnect From Healthcare Database
    Log    HIPAA audit trail verified for ${action} on patient ${patient_id}

Generate Test Report Summary
    [Documentation]    Generates summary of test execution
    
    ${end_time}=    Get Current Date
    ${duration}=    Subtract Date From Date    ${end_time}    ${TEST_START_TIME}
    
    Log    Test execution completed
    Log    Start time: ${TEST_START_TIME}
    Log    End time: ${end_time}
    Log    Duration: ${duration} seconds
    Log    Environment: ${CONFIG}[base_url]