*** Settings ***
Documentation    Environment-specific configurations for Healthcare Test Framework

*** Variables ***
# Development Environment
&{DEV_CONFIG}    
...    base_url=https://dev-healthcare.example.com
...    api_url=https://dev-api-healthcare.example.com
...    db_host=dev-db.healthcare.com
...    db_port=5432
...    db_name=healthcare_dev
...    db_user=test_user
...    db_password=test_password
...    timeout=30
...    retry_count=3

# Staging Environment  
&{STAGING_CONFIG}
...    base_url=https://staging-healthcare.example.com
...    api_url=https://staging-api-healthcare.example.com
...    db_host=staging-db.healthcare.com
...    db_port=5432
...    db_name=healthcare_staging
...    db_user=staging_user
...    db_password=staging_password
...    timeout=45
...    retry_count=2

# Production Environment (for smoke tests only)
&{PROD_CONFIG}
...    base_url=https://healthcare.example.com
...    api_url=https://api-healthcare.example.com
...    db_host=prod-db.healthcare.com
...    db_port=5432
...    db_name=healthcare_prod
...    db_user=readonly_user
...    db_password=readonly_password
...    timeout=60
...    retry_count=1

*** Keywords ***
Load Environment Configuration
    [Documentation]    Loads configuration based on environment variable
    [Arguments]    ${environment}=dev
    
    ${env_upper}=    Convert To Upper Case    ${environment}
    
    IF    '${env_upper}' == 'DEV'
        Set Global Variable    ${CONFIG}    ${DEV_CONFIG}
    ELSE IF    '${env_upper}' == 'STAGING'
        Set Global Variable    ${CONFIG}    ${STAGING_CONFIG}
    ELSE IF    '${env_upper}' == 'PROD'
        Set Global Variable    ${CONFIG}    ${PROD_CONFIG}
    ELSE
        Fail    Invalid environment: ${environment}. Valid options: dev, staging, prod
    END
    
    Set Global Variable    ${BASE_URL}       ${CONFIG}[base_url]
    Set Global Variable    ${API_BASE_URL}   ${CONFIG}[api_url]
    Set Global Variable    ${DB_HOST}        ${CONFIG}[db_host]
    Set Global Variable    ${DB_PORT}        ${CONFIG}[db_port]
    Set Global Variable    ${DB_NAME}        ${CONFIG}[db_name]
    Set Global Variable    ${DB_USER}        ${CONFIG}[db_user]
    Set Global Variable    ${DB_PASSWORD}    ${CONFIG}[db_password]
    
    Log    Environment configuration loaded: ${environment}