*** Settings ***
Library    libraries/DatabaseHealthcareLibrary.py
Resource   ../../keywords/common_keywords.robot

*** Variables ***
${DB_CONFIG}    {"db_type": "sqlite", "database": "data/healthcare.db"}

*** Test Cases ***
Test Database Connection
    [Documentation]    Test basic database connection and query
    [Tags]    database
    Connect To Healthcare Database    ${DB_CONFIG}
    ${result}=    Execute Healthcare Query    SELECT 1 as test
    Should Not Be Empty    ${result}
    Disconnect From Healthcare Database

Test Patient Data Retrieval
    [Documentation]    Test retrieving patient data from database
    [Tags]    database
    Connect To Healthcare Database    ${DB_CONFIG}
    ${patients}=    Execute Healthcare Query    SELECT * FROM patients LIMIT 5
    Should Not Be Empty    ${patients}
    Log    Retrieved ${patients.__len__()} patient records
    Disconnect From Healthcare Database

Test Appointment Data Retrieval
    [Documentation]    Test retrieving appointment data from database
    [Tags]    database
    Connect To Healthcare Database    ${DB_CONFIG}
    ${appointments}=    Execute Healthcare Query    SELECT * FROM appointments LIMIT 5
    Should Not Be Empty    ${appointments}
    Log    Retrieved ${appointments.__len__()} appointment records
    Disconnect From Healthcare Database