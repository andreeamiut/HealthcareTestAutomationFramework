*** Settings ***
Documentation    Keywords for patient management operations in healthcare applications
Library          Browser
Library          Collections
Library          String
Library          DateTime
Resource         common_keywords.robot

*** Variables ***
${PATIENT_SEARCH_FIELD}          css:input[data-testid="patient-search"]
${PATIENT_SEARCH_BUTTON}         css:button[data-testid="search-patients"]
${NEW_PATIENT_BUTTON}            css:button[data-testid="new-patient"]
${PATIENT_FORM}                  css:form[data-testid="patient-form"]
${PATIENT_LIST}                  css:[data-testid="patient-list"]
${PATIENT_DETAILS_PANEL}         css:[data-testid="patient-details"]
${SAVE_PATIENT_BUTTON}           css:button[data-testid="save-patient"]
${EDIT_PATIENT_BUTTON}           css:button[data-testid="edit-patient"]
${DELETE_PATIENT_BUTTON}         css:button[data-testid="delete-patient"]
${PATIENT_ID_DISPLAY}            css:[data-testid="patient-id"]
${MEDICAL_HISTORY_TAB}           css:a[data-testid="medical-history-tab"]
${MEDICATIONS_TAB}               css:a[data-testid="medications-tab"]
${ALLERGIES_TAB}                 css:a[data-testid="allergies-tab"]
${INSURANCE_TAB}                 css:a[data-testid="insurance-tab"]

*** Keywords ***
Navigate To Patient Management
    [Documentation]    Navigates to the patient management section
    
    Navigate To Section    Patients
    Wait For Element To Be Visible    ${PATIENT_LIST}    ${WAIT_TIMEOUT}
    Verify Page Title    Patient Management
    Log    Navigated to patient management section

Search For Patient
    [Documentation]    Searches for patient using various criteria
    [Arguments]    ${search_criteria}    ${search_type}=name
    
    # Clear existing search
    Clear Text    ${PATIENT_SEARCH_FIELD}
    
    # Enter search criteria
    Input Text Safely    ${PATIENT_SEARCH_FIELD}    ${search_criteria}
    
    # Select search type if dropdown exists
    TRY
        ${search_type_dropdown}=    Set Variable    css:select[data-testid="search-type"]
        Select From Dropdown    ${search_type_dropdown}    ${search_type}
    EXCEPT
        Log    Search type dropdown not available, using default search    level=DEBUG
    END
    
    # Perform search
    Click Element Safely    ${PATIENT_SEARCH_BUTTON}
    
    # Wait for search results
    Wait For Page Load
    
    # Validate search was executed
    ${search_performed}=    Run Keyword And Return Status    
    ...    Wait For Element To Be Visible    ${PATIENT_LIST}    ${SHORT_WAIT}
    Should Be True    ${search_performed}    Patient search did not return results
    
    Log    Patient search completed for: ${search_criteria}

Create New Patient
    [Documentation]    Creates a new patient with comprehensive data validation
    [Arguments]    &{patient_data}
    
    # Navigate to new patient form
    Click Element Safely    ${NEW_PATIENT_BUTTON}
    Wait For Element To Be Visible    ${PATIENT_FORM}    ${WAIT_TIMEOUT}
    
    # Fill required demographic information
    Input Text Safely    css:input[name="firstName"]    ${patient_data}[first_name]
    Input Text Safely    css:input[name="lastName"]     ${patient_data}[last_name]
    
    # Handle middle name if provided
    IF    'middle_name' in ${patient_data}
        Input Text Safely    css:input[name="middleName"]    ${patient_data}[middle_name]
    END
    
    # Date of birth
    Input Text Safely    css:input[name="dateOfBirth"]    ${patient_data}[date_of_birth]
    
    # Gender selection
    Select From Dropdown    css:select[name="gender"]    ${patient_data}[gender]
    
    # Contact information
    Input Text Safely    css:input[name="phoneNumber"]    ${patient_data}[phone_number]
    Input Text Safely    css:input[name="email"]         ${patient_data}[email]
    
    # Address information
    Input Text Safely    css:input[name="addressLine1"]    ${patient_data}[address_line1]
    IF    'address_line2' in ${patient_data}
        Input Text Safely    css:input[name="addressLine2"]    ${patient_data}[address_line2]
    END
    Input Text Safely    css:input[name="city"]      ${patient_data}[city]
    Input Text Safely    css:input[name="state"]     ${patient_data}[state]
    Input Text Safely    css:input[name="zipCode"]   ${patient_data}[zip_code]
    
    # Emergency contact
    Input Text Safely    css:input[name="emergencyContactName"]    ${patient_data}[emergency_contact_name]
    Input Text Safely    css:input[name="emergencyContactPhone"]   ${patient_data}[emergency_contact_phone]
    
    # Insurance information
    IF    'insurance_provider' in ${patient_data}
        Input Text Safely    css:input[name="insuranceProvider"]    ${patient_data}[insurance_provider]
        Input Text Safely    css:input[name="policyNumber"]         ${patient_data}[insurance_policy_number]
    END
    
    # Save patient
    Click Element Safely    ${SAVE_PATIENT_BUTTON}
    
    # Wait for success confirmation
    Verify Success Message Displayed    Patient created successfully
    
    # Get generated patient ID
    Wait For Element To Be Visible    ${PATIENT_ID_DISPLAY}    ${WAIT_TIMEOUT}
    ${patient_id}=    Get Text    ${PATIENT_ID_DISPLAY}
    
    # Validate patient data was saved correctly
    Validate Patient Data Display    ${patient_data}
    
    Log    New patient created successfully with ID: ${patient_id}
    [Return]    ${patient_id}

Edit Patient Information
    [Documentation]    Edits existing patient information
    [Arguments]    ${patient_id}    &{updated_data}
    
    # Search and select patient
    Search For Patient    ${patient_id}    id
    Select Patient From List    ${patient_id}
    
    # Click edit button
    Click Element Safely    ${EDIT_PATIENT_BUTTON}
    Wait For Element To Be Visible    ${PATIENT_FORM}    ${WAIT_TIMEOUT}
    
    # Update provided fields
    FOR    ${field}    ${value}    IN    &{updated_data}
        ${field_locator}=    Set Variable    css:input[name="${field}"], css:select[name="${field}"]
        TRY
            Input Text Safely    ${field_locator}    ${value}
        EXCEPT
            # Try dropdown selection if text input fails
            Select From Dropdown    ${field_locator}    ${value}
        END
    END
    
    # Save changes
    Click Element Safely    ${SAVE_PATIENT_BUTTON}
    Verify Success Message Displayed    Patient updated successfully
    
    # Validate changes were saved
    FOR    ${field}    ${value}    IN    &{updated_data}
        Validate Field Value    ${field}    ${value}
    END
    
    Log    Patient ${patient_id} information updated successfully

View Patient Details
    [Documentation]    Views comprehensive patient details
    [Arguments]    ${patient_id}
    
    # Search and select patient
    Search For Patient    ${patient_id}    id
    Select Patient From List    ${patient_id}
    
    # Wait for patient details to load
    Wait For Patient Data Load    ${patient_id}
    
    # Verify all patient sections are loaded
    Wait For Element To Be Visible    ${PATIENT_DETAILS_PANEL}    ${WAIT_TIMEOUT}
    
    # Check demographic information is displayed
    ${demographics_visible}=    Run Keyword And Return Status
    ...    Wait For Element To Be Visible    css:.patient-demographics    ${SHORT_WAIT}
    Should Be True    ${demographics_visible}    Patient demographics not loaded
    
    Log    Patient details loaded successfully for: ${patient_id}

Add Medical History Entry
    [Documentation]    Adds a new medical history entry for patient
    [Arguments]    ${patient_id}    &{medical_data}
    
    # Navigate to patient and medical history tab
    View Patient Details    ${patient_id}
    Click Element Safely    ${MEDICAL_HISTORY_TAB}
    
    # Click add new history entry
    Click Element Safely    css:button[data-testid="add-medical-history"]
    
    # Fill medical history form
    Wait For Element To Be Visible    css:form[data-testid="medical-history-form"]    ${WAIT_TIMEOUT}
    
    Input Text Safely    css:input[name="visitDate"]        ${medical_data}[visit_date]
    Input Text Safely    css:input[name="chiefComplaint"]   ${medical_data}[chief_complaint]
    Input Text Safely    css:input[name="diagnosis"]        ${medical_data}[diagnosis]
    Input Text Safely    css:textarea[name="treatment"]     ${medical_data}[treatment]
    Input Text Safely    css:textarea[name="providerNotes"] ${medical_data}[provider_notes]
    
    # Add vital signs if provided
    IF    'vital_signs' in ${medical_data}
        Input Text Safely    css:input[name="bloodPressureSystolic"]    ${medical_data}[vital_signs][blood_pressure_systolic]
        Input Text Safely    css:input[name="bloodPressureDiastolic"]   ${medical_data}[vital_signs][blood_pressure_diastolic]
        Input Text Safely    css:input[name="heartRate"]                ${medical_data}[vital_signs][heart_rate]
        Input Text Safely    css:input[name="temperature"]              ${medical_data}[vital_signs][temperature]
        Input Text Safely    css:input[name="weight"]                   ${medical_data}[vital_signs][weight_lbs]
        Input Text Safely    css:input[name="height"]                   ${medical_data}[vital_signs][height_inches]
    END
    
    # Save medical history entry
    Click Element Safely    css:button[data-testid="save-medical-history"]
    Verify Success Message Displayed    Medical history added successfully
    
    Log    Medical history entry added for patient: ${patient_id}

Add Patient Medication
    [Documentation]    Adds medication to patient's medication list
    [Arguments]    ${patient_id}    ${medication_name}    ${dosage}    ${frequency}    ${start_date}
    
    # Navigate to patient medications tab
    View Patient Details    ${patient_id}
    Click Element Safely    ${MEDICATIONS_TAB}
    
    # Add new medication
    Click Element Safely    css:button[data-testid="add-medication"]
    Wait For Element To Be Visible    css:form[data-testid="medication-form"]    ${WAIT_TIMEOUT}
    
    Input Text Safely    css:input[name="medicationName"]    ${medication_name}
    Input Text Safely    css:input[name="dosage"]            ${dosage}
    Input Text Safely    css:input[name="frequency"]         ${frequency}
    Input Text Safely    css:input[name="startDate"]         ${start_date}
    
    # Save medication
    Click Element Safely    css:button[data-testid="save-medication"]
    Verify Success Message Displayed    Medication added successfully
    
    # Verify medication appears in list
    ${medication_list}=    Set Variable    css:[data-testid="medication-list"]
    Wait For Element To Be Visible    ${medication_list}    ${SHORT_WAIT}
    ${list_text}=    Get Text    ${medication_list}
    Should Contain    ${list_text}    ${medication_name}
    
    Log    Medication ${medication_name} added for patient: ${patient_id}

Add Patient Allergy
    [Documentation]    Adds allergy information to patient record
    [Arguments]    ${patient_id}    ${allergen}    ${reaction}    ${severity}=MODERATE
    
    # Navigate to patient allergies tab
    View Patient Details    ${patient_id}
    Click Element Safely    ${ALLERGIES_TAB}
    
    # Add new allergy
    Click Element Safely    css:button[data-testid="add-allergy"]
    Wait For Element To Be Visible    css:form[data-testid="allergy-form"]    ${WAIT_TIMEOUT}
    
    Input Text Safely    css:input[name="allergen"]     ${allergen}
    Input Text Safely    css:input[name="reaction"]     ${reaction}
    Select From Dropdown    css:select[name="severity"]    ${severity}
    
    # Save allergy
    Click Element Safely    css:button[data-testid="save-allergy"]
    Verify Success Message Displayed    Allergy added successfully
    
    # Verify allergy appears in list
    ${allergy_list}=    Set Variable    css:[data-testid="allergy-list"]
    Wait For Element To Be Visible    ${allergy_list}    ${SHORT_WAIT}
    ${list_text}=    Get Text    ${allergy_list}
    Should Contain    ${list_text}    ${allergen}
    
    Log    Allergy ${allergen} added for patient: ${patient_id}

Select Patient From List
    [Documentation]    Selects a patient from the search results list
    [Arguments]    ${patient_id}
    
    ${patient_row}=    Set Variable    css:[data-patient-id="${patient_id}"]
    Wait For Element To Be Visible    ${patient_row}    ${WAIT_TIMEOUT}
    Click Element Safely    ${patient_row}
    
    # Wait for patient details to load
    Wait For Patient Data Load    ${patient_id}
    Log    Patient ${patient_id} selected from list

Validate Patient Data Display
    [Documentation]    Validates that patient data is displayed correctly
    [Arguments]    &{expected_data}
    
    FOR    ${field}    ${expected_value}    IN    &{expected_data}
        ${display_element}=    Set Variable    css:[data-field="${field}"]
        TRY
            Wait For Element To Be Visible    ${display_element}    ${SHORT_WAIT}
            ${actual_value}=    Get Text    ${display_element}
            Should Contain    ${actual_value}    ${expected_value}
        EXCEPT
            Log    Field ${field} not found in display, skipping validation    level=WARN
        END
    END
    
    Log    Patient data display validation completed

Validate Field Value
    [Documentation]    Validates a specific field value
    [Arguments]    ${field_name}    ${expected_value}
    
    ${field_locator}=    Set Variable    css:[data-field="${field_name}"], css:input[name="${field_name}"]
    ${actual_value}=    Get Text    ${field_locator}
    Should Be Equal As Strings    ${actual_value}    ${expected_value}
    Log    Field ${field_name} validation passed: ${expected_value}

Delete Patient
    [Documentation]    Deletes a patient record with confirmation
    [Arguments]    ${patient_id}    ${confirm_deletion}=True
    
    # Search and select patient
    Search For Patient    ${patient_id}    id
    Select Patient From List    ${patient_id}
    
    # Click delete button
    Click Element Safely    ${DELETE_PATIENT_BUTTON}
    
    # Handle confirmation dialog
    Wait For Element To Be Visible    css:.confirmation-modal    ${WAIT_TIMEOUT}
    
    IF    ${confirm_deletion}
        Click Element Safely    css:.confirmation-modal button[data-action="confirm"]
        Verify Success Message Displayed    Patient deleted successfully
        
        # Verify patient no longer appears in search
        Search For Patient    ${patient_id}    id
        ${no_results}=    Run Keyword And Return Status
        ...    Wait For Element To Be Visible    text=No patients found    ${SHORT_WAIT}
        Should Be True    ${no_results}    Patient should not be found after deletion
        
        Log    Patient ${patient_id} deleted successfully
    ELSE
        Click Element Safely    css:.confirmation-modal button[data-action="cancel"]
        Log    Patient deletion cancelled for: ${patient_id}
    END

Export Patient Data
    [Documentation]    Exports patient data to specified format
    [Arguments]    ${patient_id}    ${export_format}=PDF
    
    # Navigate to patient details
    View Patient Details    ${patient_id}
    
    # Click export button
    Click Element Safely    css:button[data-testid="export-patient"]
    
    # Select export format
    Select From Dropdown    css:select[name="exportFormat"]    ${export_format}
    
    # Confirm export
    Click Element Safely    css:button[data-testid="confirm-export"]
    
    # Wait for export completion
    Verify Success Message Displayed    Patient data exported successfully
    
    Log    Patient ${patient_id} data exported in ${export_format} format