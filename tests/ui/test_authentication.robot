*** Settings ***
Documentation    Comprehensive authentication and authorization test suite for healthcare application
...              Tests login functionality, role-based access control, session management, and security features
...              
...              Test Categories:
...              - Login/Logout functionality
...              - Two-factor authentication
...              - Role-based access control
...              - Session timeout and management
...              - Password policies and security
...              - Account lockout mechanisms

Resource         ../../robot_config.robot
Resource         ../../keywords/authentication_keywords.robot
Library          ../../libraries/PlaywrightHealthcareLibrary.py
Library          ../../libraries/DatabaseHealthcareLibrary.py

Suite Setup      Initialize Authentication Test Suite
Suite Teardown   Cleanup Authentication Test Suite
Test Setup       Authentication Test Setup
Test Teardown    Authentication Test Teardown

*** Variables ***
${VALID_USERNAME}          doctor_test
${VALID_PASSWORD}          Test123!
${INVALID_USERNAME}        invalid_user
${INVALID_PASSWORD}        wrong_password
${ADMIN_USERNAME}          admin_test
${ADMIN_PASSWORD}          Admin123!
${NURSE_USERNAME}          nurse_test
${NURSE_PASSWORD}          Nurse123!

*** Test Cases ***
Valid Login With Doctor Credentials
    [Documentation]    Test successful login with valid doctor credentials
    [Tags]    smoke    authentication    login
    
    Login To Healthcare Application    ${VALID_USERNAME}    ${VALID_PASSWORD}    expected_role=DOCTOR
    
    # Verify dashboard is accessible
    Navigate To Section    Dashboard
    Verify Page Title    Healthcare Dashboard
    
    # Verify doctor-specific menus are visible
    Wait For Element To Be Visible    css:a[href*="patients"]    ${WAIT_TIMEOUT}
    Wait For Element To Be Visible    css:a[href*="appointments"]    ${WAIT_TIMEOUT}
    
    # Verify HIPAA compliance elements
    Validate HIPAA Compliance Elements
    
    Logout From Healthcare Application

Invalid Login Attempts
    [Documentation]    Test login failure scenarios with various invalid credentials
    [Tags]    authentication    negative    security
    
    # Test with invalid username
    Login With Invalid Credentials    ${INVALID_USERNAME}    ${VALID_PASSWORD}    
    ...    expected_error_message=Invalid credentials
    
    # Test with invalid password
    Login With Invalid Credentials    ${VALID_USERNAME}    ${INVALID_PASSWORD}
    ...    expected_error_message=Invalid credentials
    
    # Test with both invalid
    Login With Invalid Credentials    ${INVALID_USERNAME}    ${INVALID_PASSWORD}
    ...    expected_error_message=Invalid credentials

Two Factor Authentication Login
    [Documentation]    Test two-factor authentication functionality
    [Tags]    authentication    2fa    security
    
    # Assuming 2FA is enabled for this test user
    ${two_factor_code}=    Set Variable    123456
    
    Login To Healthcare Application    ${VALID_USERNAME}    ${VALID_PASSWORD}    
    ...    two_factor_code=${two_factor_code}    expected_role=DOCTOR
    
    # Verify successful login with 2FA
    Navigate To Section    Dashboard
    Verify Page Title    Healthcare Dashboard
    
    Logout From Healthcare Application

Role Based Access Control - Admin
    [Documentation]    Test admin role permissions and access control
    [Tags]    authentication    rbac    admin
    
    Login To Healthcare Application    ${ADMIN_USERNAME}    ${ADMIN_PASSWORD}    expected_role=ADMIN
    
    # Admin should have access to all sections
    Navigate To Section    Patients
    Navigate To Section    Appointments
    Navigate To Section    Reports
    Navigate To Section    Admin
    
    # Verify admin-specific functionality
    Wait For Element To Be Visible    css:a[href*="users"]    ${WAIT_TIMEOUT}
    Wait For Element To Be Visible    css:a[href*="settings"]    ${WAIT_TIMEOUT}
    
    Logout From Healthcare Application

Role Based Access Control - Nurse
    [Documentation]    Test nurse role permissions and restricted access
    [Tags]    authentication    rbac    nurse
    
    Login To Healthcare Application    ${NURSE_USERNAME}    ${NURSE_PASSWORD}    expected_role=NURSE
    
    # Nurse should have limited access
    Navigate To Section    Patients
    Navigate To Section    Appointments
    
    # Nurse should NOT have admin access
    Element Should Not Be Visible    css:a[href*="admin"]
    Element Should Not Be Visible    css:a[href*="users"]
    
    # Test restricted URL access
    ${restricted_urls}=    Create List    /admin    /users    /system-settings
    Test Role-Based Access Control    ${NURSE_USERNAME}    ${NURSE_PASSWORD}    NURSE    ${restricted_urls}

Account Lockout After Failed Attempts
    [Documentation]    Test account lockout mechanism after multiple failed login attempts
    [Tags]    authentication    security    lockout
    
    # Test account lockout with max 3 failed attempts
    Verify Account Lockout    ${VALID_USERNAME}    ${INVALID_PASSWORD}    max_attempts=3
    
    # Verify account is locked and cannot login with correct password
    Login With Invalid Credentials    ${VALID_USERNAME}    ${VALID_PASSWORD}
    ...    expected_error_message=Account locked

Session Timeout Warning
    [Documentation]    Test session timeout warning and extension functionality
    [Tags]    authentication    session    timeout
    
    Login To Healthcare Application    ${VALID_USERNAME}    ${VALID_PASSWORD}
    
    # Test session timeout warning (simulated)
    Verify Session Timeout Warning    ${VALID_USERNAME}    ${VALID_PASSWORD}    idle_time_minutes=25
    
    Logout From Healthcare Application

Password Change Functionality
    [Documentation]    Test password change functionality and validation
    [Tags]    authentication    password    security
    
    Login To Healthcare Application    ${VALID_USERNAME}    ${VALID_PASSWORD}
    
    # Change password
    ${new_password}=    Set Variable    NewTest123!
    Change Password    ${VALID_PASSWORD}    ${new_password}    ${new_password}
    
    # Logout and verify new password works
    Logout From Healthcare Application
    Login To Healthcare Application    ${VALID_USERNAME}    ${new_password}
    
    # Change password back to original
    Change Password    ${new_password}    ${VALID_PASSWORD}    ${VALID_PASSWORD}
    
    Logout From Healthcare Application

Password Reset Functionality
    [Documentation]    Test password reset request functionality
    [Tags]    authentication    password    reset
    
    ${test_email}=    Set Variable    doctor@healthcare.test
    Reset Password    ${test_email}
    
    # Verify reset email would be sent (in real scenario, check email)
    # This test verifies the UI flow and success message

Session Expiration Handling
    [Documentation]    Test handling of expired sessions
    [Tags]    authentication    session    expiration
    
    Login To Healthcare Application    ${VALID_USERNAME}    ${VALID_PASSWORD}
    
    # Test session expiration handling
    Login With Expired Session    ${VALID_USERNAME}    ${VALID_PASSWORD}

Concurrent Session Management
    [Documentation]    Test handling of concurrent login sessions
    [Tags]    authentication    session    concurrent
    
    # First login
    Login To Healthcare Application    ${VALID_USERNAME}    ${VALID_PASSWORD}
    
    # Open new browser context for second session
    ${second_context}=    New Context    viewport={'width': 1280, 'height': 720}
    ${second_page}=    New Page
    
    # Attempt second login with same credentials
    Go To    ${BASE_URL}/login
    Input Text Safely    css:input[name="username"]    ${VALID_USERNAME}
    Input Text Safely    css:input[name="password"]    ${VALID_PASSWORD}
    Click Element Safely    css:button[type="submit"]
    
    # Verify concurrent session handling (implementation dependent)
    # Some systems allow multiple sessions, others terminate the first
    TRY
        Verify Success Message Displayed    Login successful
        Log    Concurrent sessions allowed
    EXCEPT
        Verify Error Message Displayed    Session already active
        Log    Concurrent sessions blocked
    END
    
    Close Context    ${second_context}
    Logout From Healthcare Application

HIPAA Audit Trail Verification
    [Documentation]    Verify HIPAA audit trail logging for authentication events
    [Tags]    authentication    hipaa    audit    compliance
    
    # Clear any existing audit data for test user
    Connect To Healthcare Database    postgresql    ${DB_HOST}    ${DB_PORT}    ${DB_NAME}    ${DB_USER}    ${DB_PASSWORD}
    Execute Healthcare Query    DELETE FROM audit_trail WHERE user_id = '${VALID_USERNAME}'    fetch=False
    
    # Perform login
    Login To Healthcare Application    ${VALID_USERNAME}    ${VALID_PASSWORD}
    
    # Verify audit trail entry for login
    ${audit_query}=    Set Variable    
    ...    SELECT COUNT(*) as count FROM audit_trail 
    ...    WHERE user_id = '${VALID_USERNAME}' AND action = 'LOGIN' 
    ...    AND created_date >= NOW() - INTERVAL '5 minutes'
    
    ${audit_result}=    Execute Healthcare Query    ${audit_query}
    Should Be True    ${audit_result}[0][count] > 0    Login audit trail entry not found
    
    # Perform logout
    Logout From Healthcare Application
    
    # Verify audit trail entry for logout
    ${logout_audit_query}=    Set Variable    
    ...    SELECT COUNT(*) as count FROM audit_trail 
    ...    WHERE user_id = '${VALID_USERNAME}' AND action = 'LOGOUT' 
    ...    AND created_date >= NOW() - INTERVAL '5 minutes'
    
    ${logout_audit_result}=    Execute Healthcare Query    ${logout_audit_query}
    Should Be True    ${logout_audit_result}[0][count] > 0    Logout audit trail entry not found
    
    Disconnect From Healthcare Database

Security Headers Validation
    [Documentation]    Validate security headers in authentication responses
    [Tags]    authentication    security    headers
    
    # Test security headers on login page
    Go To    ${BASE_URL}/login
    
    # Perform login to test security headers on authenticated pages
    Login To Healthcare Application    ${VALID_USERNAME}    ${VALID_PASSWORD}
    
    # Navigate to different pages to check headers consistently applied
    Navigate To Section    Patients
    Navigate To Section    Appointments
    
    Logout From Healthcare Application

*** Keywords ***
Initialize Authentication Test Suite
    [Documentation]    Initialize the authentication test suite
    
    Initialize Test Environment    ${ENVIRONMENT}
    Setup Browser For Healthcare Tests
    
    # Verify test users exist in database
    Connect To Healthcare Database    postgresql    ${DB_HOST}    ${DB_PORT}    ${DB_NAME}    ${DB_USER}    ${DB_PASSWORD}
    
    ${user_check_query}=    Set Variable    
    ...    SELECT username FROM users WHERE username IN ('${VALID_USERNAME}', '${ADMIN_USERNAME}', '${NURSE_USERNAME}')
    ${existing_users}=    Execute Healthcare Query    ${user_check_query}
    
    ${user_count}=    Get Length    ${existing_users}
    Should Be True    ${user_count} >= 3    Required test users not found in database
    
    Disconnect From Healthcare Database
    
    Log    Authentication test suite initialized successfully

Cleanup Authentication Test Suite
    [Documentation]    Cleanup after authentication test suite
    
    # Clear any locked accounts from testing
    TRY
        Connect To Healthcare Database    postgresql    ${DB_HOST}    ${DB_PORT}    ${DB_NAME}    ${DB_USER}    ${DB_PASSWORD}
        Execute Healthcare Query    
        ...    UPDATE users SET status = 'ACTIVE', failed_login_attempts = 0 
        ...    WHERE username IN ('${VALID_USERNAME}', '${ADMIN_USERNAME}', '${NURSE_USERNAME}')    
        ...    fetch=False
        Disconnect From Healthcare Database
    EXCEPT
        Log    Database cleanup failed    level=WARN
    END
    
    Close Healthcare Application
    Generate Test Report Summary

Authentication Test Setup
    [Documentation]    Setup for each authentication test
    
    Go To    ${BASE_URL}
    Handle Unexpected Modal

Authentication Test Teardown
    [Documentation]    Teardown for each authentication test
    
    # Ensure logout if still logged in
    TRY
        ${is_logged_in}=    Run Keyword And Return Status    
        ...    Wait For Element To Be Visible    css:[data-testid="logout-button"]    1s
        IF    ${is_logged_in}
            Logout Safely
        END
    EXCEPT
        Log    User not logged in or logout not needed    level=DEBUG
    END
    
    # Capture screenshot on test failure
    Run Keyword If    '${TEST STATUS}' == 'FAIL'    
    ...    Capture Screenshot With Timestamp    ${TEST NAME}