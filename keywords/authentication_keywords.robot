*** Settings ***
Documentation    Keywords for authentication and authorization testing in healthcare applications
Library          Browser
Library          Collections
Library          String
Resource         common_keywords.robot

*** Variables ***
${LOGIN_FORM}                css:form[data-testid="login-form"]
${USERNAME_FIELD}            css:input[name="username"]
${PASSWORD_FIELD}            css:input[name="password"]
${TWO_FACTOR_FIELD}          css:input[name="twoFactor"]
${LOGIN_BUTTON}              css:button[type="submit"]
${LOGOUT_BUTTON}             css:[data-testid="logout-button"]
${FORGOT_PASSWORD_LINK}      css:a[href*="forgot-password"]
${DASHBOARD_INDICATOR}       css:[data-testid="dashboard"]
${ROLE_SELECTOR}             css:select[name="role"]
${SESSION_TIMEOUT_MODAL}     css:.session-timeout-modal

*** Keywords ***
Login To Healthcare Application
    [Documentation]    Performs login to healthcare application with comprehensive validation
    [Arguments]    ${username}    ${password}    ${two_factor_code}=${EMPTY}    ${expected_role}=${EMPTY}
    
    # Navigate to login page if not already there
    ${current_url}=    Get Url
    ${is_login_page}=    Run Keyword And Return Status    Should Contain    ${current_url}    login
    IF    not ${is_login_page}
        Go To    ${BASE_URL}/login
        Wait For Page Load
    END
    
    # Verify login form is present
    Wait For Element To Be Visible    ${LOGIN_FORM}    ${WAIT_TIMEOUT}
    
    # Clear any existing data
    Clear Text    ${USERNAME_FIELD}
    Clear Text    ${PASSWORD_FIELD}
    
    # Enter credentials
    Input Text Safely    ${USERNAME_FIELD}    ${username}
    Input Text Safely    ${PASSWORD_FIELD}    ${password}
    
    # Handle two-factor authentication if provided
    IF    '${two_factor_code}' != '${EMPTY}'
        Wait For Element To Be Visible    ${TWO_FACTOR_FIELD}    ${SHORT_WAIT}
        Input Text Safely    ${TWO_FACTOR_FIELD}    ${two_factor_code}
    END
    
    # Submit login form
    Click Element Safely    ${LOGIN_BUTTON}
    
    # Wait for login to complete
    Wait For Element To Be Visible    ${DASHBOARD_INDICATOR}    ${WAIT_TIMEOUT}
    
    # Verify successful login
    ${current_url}=    Get Url
    Should Not Contain    ${current_url}    login    Login failed - still on login page
    
    # Verify user role if specified
    IF    '${expected_role}' != '${EMPTY}'
        Verify User Role    ${expected_role}
    END
    
    # Validate HIPAA compliance elements
    Validate HIPAA Compliance Elements
    
    Log    Successfully logged in as: ${username}
    Capture Screenshot With Timestamp    login_success

Login With Invalid Credentials
    [Documentation]    Attempts login with invalid credentials and verifies failure
    [Arguments]    ${username}    ${password}    ${expected_error_message}=Invalid credentials
    
    Go To    ${BASE_URL}/login
    Wait For Page Load
    
    Input Text Safely    ${USERNAME_FIELD}    ${username}
    Input Text Safely    ${PASSWORD_FIELD}    ${password}
    Click Element Safely    ${LOGIN_BUTTON}
    
    # Verify error message is displayed
    Verify Error Message Displayed    ${expected_error_message}
    
    # Verify user is still on login page
    ${current_url}=    Get Url
    Should Contain    ${current_url}    login    User should remain on login page after failed login
    
    Log    Invalid login attempt verified for: ${username}

Login With Expired Session
    [Documentation]    Tests behavior when session expires
    [Arguments]    ${username}    ${password}
    
    # Login normally first
    Login To Healthcare Application    ${username}    ${password}
    
    # Simulate session expiration (if endpoint available)
    TRY
        ${session_endpoint}=    Set Variable    ${API_BASE_URL}/auth/expire-session
        POST Healthcare API    /auth/expire-session    {}    expected_status=200
    EXCEPT
        Log    Session expiration endpoint not available, skipping simulation    level=WARN
    END
    
    # Try to access protected resource
    Go To    ${BASE_URL}/patients
    
    # Should be redirected to login or see session timeout modal
    TRY
        Wait For Element To Be Visible    ${SESSION_TIMEOUT_MODAL}    ${SHORT_WAIT}
        Click Element Safely    css:.modal .btn-primary    # Click "Login Again" button
    EXCEPT
        # Alternative: Check if redirected to login page
        ${current_url}=    Get Url
        Should Contain    ${current_url}    login    Should be redirected to login page
    END
    
    Log    Session expiration handling verified

Verify User Role
    [Documentation]    Verifies the current user's role and permissions
    [Arguments]    ${expected_role}
    
    # Check role indicator in header/navigation
    ${role_indicator}=    Set Variable    css:[data-testid="user-role"]
    Wait For Element To Be Visible    ${role_indicator}    ${WAIT_TIMEOUT}
    ${displayed_role}=    Get Text    ${role_indicator}
    Should Be Equal As Strings    ${displayed_role}    ${expected_role}
    
    # Verify role-specific menu items are visible
    IF    '${expected_role}' == 'ADMIN'
        Wait For Element To Be Visible    css:a[href*="admin"]    ${SHORT_WAIT}
        Wait For Element To Be Visible    css:a[href*="users"]    ${SHORT_WAIT}
    ELSE IF    '${expected_role}' == 'DOCTOR'
        Wait For Element To Be Visible    css:a[href*="patients"]    ${SHORT_WAIT}
        Wait For Element To Be Visible    css:a[href*="appointments"]    ${SHORT_WAIT}
    ELSE IF    '${expected_role}' == 'NURSE'
        Wait For Element To Be Visible    css:a[href*="patients"]    ${SHORT_WAIT}
        Element Should Not Be Visible    css:a[href*="admin"]
    ELSE IF    '${expected_role}' == 'RECEPTIONIST'
        Wait For Element To Be Visible    css:a[href*="appointments"]    ${SHORT_WAIT}
        Wait For Element To Be Visible    css:a[href*="scheduling"]    ${SHORT_WAIT}
        Element Should Not Be Visible    css:a[href*="medical-records"]
    END
    
    Log    User role verified: ${expected_role}

Test Role-Based Access Control
    [Documentation]    Tests access control for different user roles
    [Arguments]    ${username}    ${password}    ${role}    ${restricted_urls}
    
    Login To Healthcare Application    ${username}    ${password}    expected_role=${role}
    
    # Test access to restricted URLs
    FOR    ${url}    IN    @{restricted_urls}
        Go To    ${BASE_URL}${url}
        ${current_url}=    Get Url
        
        # Should be redirected to access denied or login page
        ${is_access_denied}=    Run Keyword And Return Status    
        ...    Should Contain Any    ${current_url}    access-denied    unauthorized    login
        
        IF    not ${is_access_denied}
            # Check for access denied message on the page
            ${access_denied_present}=    Run Keyword And Return Status
            ...    Wait For Element To Be Visible    text=Access Denied    ${SHORT_WAIT}
            Should Be True    ${access_denied_present}    
            ...    User ${role} should not have access to ${url}
        END
        
        Log    Access control verified for ${role} accessing ${url}
    END

Change Password
    [Documentation]    Changes user password with validation
    [Arguments]    ${current_password}    ${new_password}    ${confirm_password}
    
    # Navigate to profile/settings page
    Navigate To Section    Profile
    
    # Click change password option
    Click Element Safely    css:button[data-testid="change-password"]
    
    # Fill password change form
    Wait For Element To Be Visible    css:input[name="currentPassword"]    ${WAIT_TIMEOUT}
    Input Text Safely    css:input[name="currentPassword"]    ${current_password}
    Input Text Safely    css:input[name="newPassword"]    ${new_password}
    Input Text Safely    css:input[name="confirmPassword"]    ${confirm_password}
    
    # Submit form
    Click Element Safely    css:button[type="submit"]
    
    # Verify success message
    Verify Success Message Displayed    Password changed successfully
    
    Log    Password changed successfully

Reset Password
    [Documentation]    Tests password reset functionality
    [Arguments]    ${email}
    
    Go To    ${BASE_URL}/login
    Wait For Page Load
    
    # Click forgot password link
    Click Element Safely    ${FORGOT_PASSWORD_LINK}
    
    # Enter email for password reset
    Wait For Element To Be Visible    css:input[name="email"]    ${WAIT_TIMEOUT}
    Input Text Safely    css:input[name="email"]    ${email}
    
    # Submit reset request
    Click Element Safely    css:button[type="submit"]
    
    # Verify confirmation message
    Verify Success Message Displayed    Password reset email sent
    
    Log    Password reset initiated for: ${email}

Verify Account Lockout
    [Documentation]    Tests account lockout after multiple failed attempts
    [Arguments]    ${username}    ${wrong_password}    ${max_attempts}=3
    
    Go To    ${BASE_URL}/login
    
    # Attempt login multiple times with wrong password
    FOR    ${attempt}    IN RANGE    1    ${max_attempts + 1}
        Wait For Page Load
        Input Text Safely    ${USERNAME_FIELD}    ${username}
        Input Text Safely    ${PASSWORD_FIELD}    ${wrong_password}
        Click Element Safely    ${LOGIN_BUTTON}
        
        IF    ${attempt} < ${max_attempts}
            Verify Error Message Displayed    Invalid credentials
            # Clear fields for next attempt
            Clear Text    ${USERNAME_FIELD}
            Clear Text    ${PASSWORD_FIELD}
        END
    END
    
    # Final attempt should show account locked message
    Verify Error Message Displayed    Account locked
    
    Log    Account lockout verified after ${max_attempts} failed attempts

Verify Session Timeout Warning
    [Documentation]    Tests session timeout warning functionality
    [Arguments]    ${username}    ${password}    ${idle_time_minutes}=25
    
    Login To Healthcare Application    ${username}    ${password}
    
    # Simulate idle time (this would typically be done through JavaScript)
    Execute Javascript    
    ...    setTimeout(() => { 
    ...        window.sessionStorage.setItem('lastActivity', Date.now() - ${idle_time_minutes * 60000}); 
    ...    }, 1000);
    
    # Navigate to trigger session check
    Go To    ${BASE_URL}/patients
    
    # Should see session timeout warning
    Wait For Element To Be Visible    ${SESSION_TIMEOUT_MODAL}    ${WAIT_TIMEOUT}
    
    # Verify warning message content
    ${warning_text}=    Get Text    ${SESSION_TIMEOUT_MODAL}
    Should Contain    ${warning_text}    session will expire
    
    # Click "Stay Logged In" to extend session
    Click Element Safely    css:.modal button[data-action="extend"]
    Wait For Element To Be Hidden    ${SESSION_TIMEOUT_MODAL}    ${SHORT_WAIT}
    
    Log    Session timeout warning verified and session extended

Logout From Healthcare Application
    [Documentation]    Performs secure logout with validation
    
    # Click logout button
    Click Element Safely    ${LOGOUT_BUTTON}
    
    # Wait for redirect to login page
    Wait For Element To Be Visible    ${LOGIN_FORM}    ${WAIT_TIMEOUT}
    
    # Verify logout was successful
    ${current_url}=    Get Url
    Should Contain    ${current_url}    login    Should be redirected to login page
    
    # Verify session is cleared by trying to access protected page
    Go To    ${BASE_URL}/dashboard
    ${current_url}=    Get Url
    Should Contain    ${current_url}    login    Should be redirected to login for protected page
    
    Log    Logout completed successfully