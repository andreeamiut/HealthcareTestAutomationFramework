*** Settings ***
Documentation    Comprehensive patient management test suite for healthcare application
...              Tests patient creation, search, update, deletion, and data integrity
...              
...              Test Categories:
...              - Patient creation and data validation
...              - Patient search and retrieval
...              - Patient information updates
...              - Medical history management
...              - Medication and allergy tracking
...              - Data integrity and HIPAA compliance

Resource         ../../robot_config.robot
Resource         ../../keywords/authentication_keywords.robot
Resource         ../../keywords/patient_keywords.robot
Library          ../../libraries/PlaywrightHealthcareLibrary.py
Library          ../../libraries/DatabaseHealthcareLibrary.py
Variables        ../../data/test_data/sample_patients.json

Suite Setup      Initialize Patient Management Test Suite
Suite Teardown   Cleanup Patient Management Test Suite
Test Setup       Patient Management Test Setup
Test Teardown    Patient Management Test Teardown

*** Variables ***
${TEST_PATIENT_ID}         ${EMPTY}
${CREATED_PATIENT_IDS}     @{EMPTY}

*** Test Cases ***
Create New Patient With Complete Information
    [Documentation]    Test creating a new patient with all required and optional information
    [Tags]    smoke    patient    creation
    
    Navigate To Patient Management
    
    # Generate comprehensive test patient data
    &{patient_data}=    Create Dictionary
    ...    first_name=John
    ...    last_name=TestPatient
    ...    middle_name=Michael
    ...    date_of_birth=1985-06-15
    ...    gender=M
    ...    phone_number=555-0199
    ...    email=john.testpatient@test.com
    ...    address_line1=123 Test Street
    ...    address_line2=Unit 5A
    ...    city=Test City
    ...    state=IL
    ...    zip_code=60601
    ...    emergency_contact_name=Jane TestPatient
    ...    emergency_contact_phone=555-0200
    ...    insurance_provider=Test Insurance Co
    ...    insurance_policy_number=TEST123456789
    
    ${patient_id}=    Create New Patient    &{patient_data}
    Set Suite Variable    ${TEST_PATIENT_ID}    ${patient_id}
    Append To List    ${CREATED_PATIENT_IDS}    ${patient_id}
    
    # Verify patient was created in database
    Connect To Healthcare Database    postgresql    ${DB_HOST}    ${DB_PORT}    ${DB_NAME}    ${DB_USER}    ${DB_PASSWORD}
    ${db_validation}=    Validate Patient Data Integrity    ${patient_id}
    Should Be True    ${db_validation}[patient_exists]    Patient not found in database
    Should Be True    ${db_validation}[has_required_fields]    Required fields missing in database
    Disconnect From Healthcare Database
    
    Log    Patient created successfully with ID: ${patient_id}

Create Patient With Minimal Required Information
    [Documentation]    Test creating a patient with only required fields
    [Tags]    patient    creation    minimal
    
    Navigate To Patient Management
    
    &{minimal_patient_data}=    Create Dictionary
    ...    first_name=Jane
    ...    last_name=MinimalTest
    ...    date_of_birth=1990-03-22
    ...    gender=F
    ...    phone_number=555-0201
    
    ${patient_id}=    Create New Patient    &{minimal_patient_data}
    Append To List    ${CREATED_PATIENT_IDS}    ${patient_id}
    
    # Verify patient creation with minimal data
    View Patient Details    ${patient_id}
    Validate Patient Data Display    &{minimal_patient_data}
    
    Log    Minimal patient created successfully with ID: ${patient_id}

Search Patient By Name
    [Documentation]    Test patient search functionality using patient name
    [Tags]    patient    search
    
    Navigate To Patient Management
    
    # Search for existing test patient
    Search For Patient    TestPatient    name
    
    # Verify search results contain expected patient
    ${search_results}=    Get Text    ${PATIENT_LIST}
    Should Contain    ${search_results}    TestPatient
    
    Log    Patient search by name completed successfully

Search Patient By ID
    [Documentation]    Test patient search functionality using patient ID
    [Tags]    patient    search
    
    Navigate To Patient Management
    
    # Use the patient ID from the first test
    Search For Patient    ${TEST_PATIENT_ID}    id
    
    # Select patient from search results
    Select Patient From List    ${TEST_PATIENT_ID}
    
    # Verify patient details are displayed
    Wait For Element To Be Visible    ${PATIENT_DETAILS_PANEL}    ${WAIT_TIMEOUT}
    
    Log    Patient search by ID completed successfully

Update Patient Information
    [Documentation]    Test updating existing patient information
    [Tags]    patient    update
    
    # Updated information
    &{updated_data}=    Create Dictionary
    ...    phone_number=555-0299
    ...    email=john.updated@test.com
    ...    address_line1=456 Updated Street
    
    Edit Patient Information    ${TEST_PATIENT_ID}    &{updated_data}
    
    # Verify updates were saved
    View Patient Details    ${TEST_PATIENT_ID}
    Validate Patient Data Display    &{updated_data}
    
    # Verify database was updated
    Connect To Healthcare Database    postgresql    ${DB_HOST}    ${DB_PORT}    ${DB_NAME}    ${DB_USER}    ${DB_PASSWORD}
    ${update_query}=    Set Variable    
    ...    SELECT phone_number, email, address_line1 FROM patients WHERE patient_id = '${TEST_PATIENT_ID}'
    ${db_result}=    Execute Healthcare Query    ${update_query}
    
    Should Be Equal    ${db_result}[0][phone_number]    ${updated_data}[phone_number]
    Should Be Equal    ${db_result}[0][email]          ${updated_data}[email]
    Should Be Equal    ${db_result}[0][address_line1]  ${updated_data}[address_line1]
    
    Disconnect From Healthcare Database
    
    Log    Patient information updated successfully

Add Medical History Entry
    [Documentation]    Test adding medical history to patient record
    [Tags]    patient    medical_history
    
    &{medical_data}=    Create Dictionary
    ...    visit_date=2024-01-15
    ...    chief_complaint=Annual physical examination
    ...    diagnosis=Routine health maintenance
    ...    treatment=Preventive care counseling
    ...    provider_notes=Patient in good health, all vitals normal
    ...    vital_signs=${DICT_WITH_VITALS}
    
    &{vital_signs}=    Create Dictionary
    ...    blood_pressure_systolic=120
    ...    blood_pressure_diastolic=80
    ...    heart_rate=72
    ...    temperature=98.6
    ...    weight_lbs=180
    ...    height_inches=70
    
    Set To Dictionary    ${medical_data}    vital_signs    ${vital_signs}
    
    Add Medical History Entry    ${TEST_PATIENT_ID}    &{medical_data}
    
    # Verify medical history was added
    View Patient Details    ${TEST_PATIENT_ID}
    Click Element Safely    ${MEDICAL_HISTORY_TAB}
    
    ${history_content}=    Get Text    css:.medical-history-section
    Should Contain    ${history_content}    Annual physical examination
    Should Contain    ${history_content}    Routine health maintenance
    
    Log    Medical history entry added successfully

Add Patient Medication
    [Documentation]    Test adding medication to patient's medication list
    [Tags]    patient    medications
    
    Add Patient Medication    ${TEST_PATIENT_ID}    Lisinopril    10mg    Once daily    2024-01-15
    
    # Verify medication was added
    View Patient Details    ${TEST_PATIENT_ID}
    Click Element Safely    ${MEDICATIONS_TAB}
    
    ${medications_content}=    Get Text    css:.medications-section
    Should Contain    ${medications_content}    Lisinopril
    Should Contain    ${medications_content}    10mg
    Should Contain    ${medications_content}    Once daily
    
    Log    Patient medication added successfully

Add Patient Allergy
    [Documentation]    Test adding allergy information to patient record
    [Tags]    patient    allergies
    
    Add Patient Allergy    ${TEST_PATIENT_ID}    Penicillin    Skin rash    MODERATE
    
    # Verify allergy was added
    View Patient Details    ${TEST_PATIENT_ID}
    Click Element Safely    ${ALLERGIES_TAB}
    
    ${allergies_content}=    Get Text    css:.allergies-section
    Should Contain    ${allergies_content}    Penicillin
    Should Contain    ${allergies_content}    Skin rash
    Should Contain    ${allergies_content}    MODERATE
    
    Log    Patient allergy added successfully

Validate Patient Data Integrity
    [Documentation]    Test comprehensive patient data integrity validation
    [Tags]    patient    integrity    validation
    
    Connect To Healthcare Database    postgresql    ${DB_HOST}    ${DB_PORT}    ${DB_NAME}    ${DB_USER}    ${DB_PASSWORD}
    
    ${integrity_results}=    Validate Patient Data Integrity    ${TEST_PATIENT_ID}
    
    # Verify all integrity checks pass
    Should Be True    ${integrity_results}[patient_exists]         Patient should exist
    Should Be True    ${integrity_results}[has_required_fields]    Required fields should be present
    Should Be True    ${integrity_results}[data_integrity_passed] Overall integrity should pass
    
    # Check related records exist
    Should Be True    ${integrity_results}[medical_records_count] >= 1    Medical records should exist
    Should Be True    ${integrity_results}[prescriptions_count] >= 1     Medications should exist
    
    Disconnect From Healthcare Database
    
    Log    Patient data integrity validation completed successfully

Export Patient Data
    [Documentation]    Test patient data export functionality
    [Tags]    patient    export
    
    Export Patient Data    ${TEST_PATIENT_ID}    PDF
    
    # Verify export success message was displayed
    # In a real implementation, you might also verify the file was created
    
    Log    Patient data export completed successfully

Patient Data Privacy Validation
    [Documentation]    Test patient data privacy and HIPAA compliance features
    [Tags]    patient    privacy    hipaa    compliance
    
    View Patient Details    ${TEST_PATIENT_ID}
    
    # Verify sensitive data is properly protected
    ${ssn_field}=    Get Text    css:[data-field="social_security_number"]
    Should Match Regexp    ${ssn_field}    \\*\\*\\*-\\*\\*-\\d{4}    SSN should be masked
    
    # Verify HIPAA audit trail for patient access
    Connect To Healthcare Database    postgresql    ${DB_HOST}    ${DB_PORT}    ${DB_NAME}    ${DB_USER}    ${DB_PASSWORD}
    Verify HIPAA Audit Trail    ${TEST_PATIENT_ID}    READ    doctor_test
    Disconnect From Healthcare Database
    
    Log    Patient data privacy validation completed successfully

Bulk Patient Data Operations
    [Documentation]    Test bulk operations on patient data
    [Tags]    patient    bulk    performance
    
    Navigate To Patient Management
    
    # Create multiple patients for bulk testing
    ${bulk_patient_ids}=    Create List
    
    FOR    ${i}    IN RANGE    1    6
        &{bulk_patient_data}=    Create Dictionary
        ...    first_name=BulkTest${i}
        ...    last_name=Patient
        ...    date_of_birth=199${i}-01-01
        ...    gender=M
        ...    phone_number=555-010${i}
        ...    email=bulktest${i}@test.com
        
        ${bulk_patient_id}=    Create New Patient    &{bulk_patient_data}
        Append To List    ${bulk_patient_ids}    ${bulk_patient_id}
        Append To List    ${CREATED_PATIENT_IDS}    ${bulk_patient_id}
    END
    
    # Test bulk search
    Search For Patient    BulkTest    name
    
    ${search_results}=    Get Text    ${PATIENT_LIST}
    Should Contain    ${search_results}    BulkTest1
    Should Contain    ${search_results}    BulkTest5
    
    Log    Bulk patient operations completed successfully

Delete Patient Record
    [Documentation]    Test patient record deletion with proper confirmation
    [Tags]    patient    deletion
    
    # Create a patient specifically for deletion testing
    &{delete_test_patient}=    Create Dictionary
    ...    first_name=Delete
    ...    last_name=TestPatient
    ...    date_of_birth=1985-12-25
    ...    gender=F
    ...    phone_number=555-0999
    
    ${delete_patient_id}=    Create New Patient    &{delete_test_patient}
    
    # Delete the patient
    Delete Patient    ${delete_patient_id}    confirm_deletion=True
    
    # Verify patient was deleted from database
    Connect To Healthcare Database    postgresql    ${DB_HOST}    ${DB_PORT}    ${DB_NAME}    ${DB_USER}    ${DB_PASSWORD}
    ${deletion_check}=    Execute Healthcare Query    
    ...    SELECT COUNT(*) as count FROM patients WHERE patient_id = '${delete_patient_id}'
    Should Be Equal As Numbers    ${deletion_check}[0][count]    0    Patient should be deleted from database
    Disconnect From Healthcare Database
    
    Log    Patient record deletion completed successfully

*** Keywords ***
Initialize Patient Management Test Suite
    [Documentation]    Initialize the patient management test suite
    
    Initialize Test Environment    ${ENVIRONMENT}
    Setup Browser For Healthcare Tests
    
    # Login as doctor for patient management tests
    Login To Healthcare Application    doctor_test    Test123!    expected_role=DOCTOR
    
    # Initialize created patients list
    ${empty_list}=    Create List
    Set Suite Variable    ${CREATED_PATIENT_IDS}    ${empty_list}
    
    Log    Patient management test suite initialized successfully

Cleanup Patient Management Test Suite
    [Documentation]    Cleanup after patient management test suite
    
    # Clean up all created patients
    IF    ${CREATED_PATIENT_IDS}
        Connect To Healthcare Database    postgresql    ${DB_HOST}    ${DB_PORT}    ${DB_NAME}    ${DB_USER}    ${DB_PASSWORD}
        Cleanup Test Data    ${CREATED_PATIENT_IDS}
        Disconnect From Healthcare Database
        Log    Cleaned up ${CREATED_PATIENT_IDS.__len__()} test patients
    END
    
    Logout From Healthcare Application
    Close Healthcare Application
    Generate Test Report Summary

Patient Management Test Setup
    [Documentation]    Setup for each patient management test
    
    Go To    ${BASE_URL}/dashboard
    Handle Unexpected Modal

Patient Management Test Teardown
    [Documentation]    Teardown for each patient management test
    
    # Capture screenshot on test failure
    Run Keyword If    '${TEST STATUS}' == 'FAIL'    
    ...    Capture Screenshot With Timestamp    ${TEST NAME}
    
    # Return to dashboard for next test
    TRY
        Navigate To Section    Dashboard
    EXCEPT
        Log    Unable to return to dashboard    level=WARN
    END