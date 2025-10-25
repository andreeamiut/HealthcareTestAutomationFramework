*** Settings ***
Documentation    Keywords for appointment management and scheduling in healthcare applications
Library          Browser
Library          Collections
Library          String
Library          DateTime
Resource         common_keywords.robot

*** Variables ***
${APPOINTMENTS_SECTION}          css:[data-testid="appointments-section"]
${APPOINTMENT_CALENDAR}          css:[data-testid="appointment-calendar"]
${NEW_APPOINTMENT_BUTTON}        css:button[data-testid="new-appointment"]
${APPOINTMENT_FORM}              css:form[data-testid="appointment-form"]
${APPOINTMENT_LIST}              css:[data-testid="appointment-list"]
${APPOINTMENT_SEARCH_FIELD}      css:input[data-testid="appointment-search"]
${SAVE_APPOINTMENT_BUTTON}       css:button[data-testid="save-appointment"]
${EDIT_APPOINTMENT_BUTTON}       css:button[data-testid="edit-appointment"]
${CANCEL_APPOINTMENT_BUTTON}     css:button[data-testid="cancel-appointment"]
${APPOINTMENT_DETAILS_PANEL}     css:[data-testid="appointment-details"]
${TIME_SLOT_SELECTOR}            css:select[data-testid="time-slot"]
${PROVIDER_SELECTOR}             css:select[data-testid="provider"]
${APPOINTMENT_TYPE_SELECTOR}     css:select[data-testid="appointment-type"]
${PATIENT_LOOKUP}                css:input[data-testid="patient-lookup"]
${SCHEDULE_CONFLICT_MODAL}       css:.schedule-conflict-modal

*** Keywords ***
Navigate To Appointment Management
    [Documentation]    Navigates to the appointment management section
    
    Navigate To Section    Appointments
    Wait For Element To Be Visible    ${APPOINTMENTS_SECTION}    ${WAIT_TIMEOUT}
    Verify Page Title    Appointment Management
    Log    Navigated to appointment management section

View Appointment Calendar
    [Documentation]    Views the appointment calendar for a specific date
    [Arguments]    ${target_date}=${EMPTY}
    
    Navigate To Appointment Management
    Wait For Element To Be Visible    ${APPOINTMENT_CALENDAR}    ${WAIT_TIMEOUT}
    
    # Navigate to specific date if provided
    IF    '${target_date}' != '${EMPTY}'
        ${date_picker}=    Set Variable    css:input[data-testid="calendar-date"]
        Input Text Safely    ${date_picker}    ${target_date}
        Click Element Safely    css:button[data-testid="go-to-date"]
        Wait For Page Load
    END
    
    # Verify calendar is loaded
    ${calendar_loaded}=    Run Keyword And Return Status
    ...    Wait For Element To Be Visible    css:.calendar-grid    ${SHORT_WAIT}
    Should Be True    ${calendar_loaded}    Appointment calendar failed to load
    
    Log    Appointment calendar loaded for date: ${target_date}

Schedule New Appointment
    [Documentation]    Schedules a new appointment with comprehensive validation
    [Arguments]    &{appointment_data}
    
    # Navigate to appointment form
    Navigate To Appointment Management
    Click Element Safely    ${NEW_APPOINTMENT_BUTTON}
    Wait For Element To Be Visible    ${APPOINTMENT_FORM}    ${WAIT_TIMEOUT}
    
    # Search and select patient
    Input Text Safely    ${PATIENT_LOOKUP}    ${appointment_data}[patient_id]
    Click Element Safely    css:button[data-testid="search-patient"]
    
    # Wait for patient to be found and selected
    Wait For Element To Be Visible    css:.patient-selected    ${WAIT_TIMEOUT}
    
    # Select appointment type
    Select From Dropdown    ${APPOINTMENT_TYPE_SELECTOR}    ${appointment_data}[appointment_type]
    
    # Select provider
    Select From Dropdown    ${PROVIDER_SELECTOR}    ${appointment_data}[provider_id]
    
    # Set appointment date
    Input Text Safely    css:input[name="appointmentDate"]    ${appointment_data}[appointment_date]
    
    # Check available time slots and select
    Click Element Safely    css:button[data-testid="check-availability"]
    Wait For Element To Be Visible    ${TIME_SLOT_SELECTOR}    ${WAIT_TIMEOUT}
    
    # Select preferred time slot
    Select From Dropdown    ${TIME_SLOT_SELECTOR}    ${appointment_data}[time_slot]
    
    # Set duration
    Select From Dropdown    css:select[name="duration"]    ${appointment_data}[duration_minutes]
    
    # Add appointment notes if provided
    IF    'notes' in ${appointment_data}
        Input Text Safely    css:textarea[name="appointmentNotes"]    ${appointment_data}[notes]
    END
    
    # Set appointment priority if provided
    IF    'priority' in ${appointment_data}
        Select From Dropdown    css:select[name="priority"]    ${appointment_data}[priority]
    END
    
    # Save appointment
    Click Element Safely    ${SAVE_APPOINTMENT_BUTTON}
    
    # Handle potential scheduling conflicts
    ${conflict_detected}=    Run Keyword And Return Status
    ...    Wait For Element To Be Visible    ${SCHEDULE_CONFLICT_MODAL}    ${SHORT_WAIT}
    
    IF    ${conflict_detected}
        Handle Scheduling Conflict    ${appointment_data}
    END
    
    # Verify appointment was created successfully
    Verify Success Message Displayed    Appointment scheduled successfully
    
    # Get generated appointment ID
    ${appointment_id}=    Get Text    css:[data-testid="appointment-id"]
    
    Log    New appointment scheduled successfully with ID: ${appointment_id}
    [Return]    ${appointment_id}

Handle Scheduling Conflict
    [Documentation]    Handles scheduling conflicts when they occur
    [Arguments]    &{appointment_data}
    
    # Check conflict details
    ${conflict_message}=    Get Text    ${SCHEDULE_CONFLICT_MODAL}
    Log    Scheduling conflict detected: ${conflict_message}    level=WARN
    
    # Look for alternative time slots
    ${alternative_slots_available}=    Run Keyword And Return Status
    ...    Wait For Element To Be Visible    css:.alternative-slots    ${SHORT_WAIT}
    
    IF    ${alternative_slots_available}
        # Select first available alternative
        Click Element Safely    css:.alternative-slots .time-slot:first-child
        Click Element Safely    css:button[data-action="accept-alternative"]
        Log    Alternative time slot selected to resolve conflict
    ELSE
        # Force scheduling or cancel
        IF    'force_schedule' in ${appointment_data} and ${appointment_data}[force_schedule]
            Click Element Safely    css:button[data-action="force-schedule"]
            Log    Appointment forced despite conflict    level=WARN
        ELSE
            Click Element Safely    css:button[data-action="cancel"]
            Fail    Appointment scheduling cancelled due to conflict
        END
    END

Search For Appointment
    [Documentation]    Searches for appointments using various criteria
    [Arguments]    ${search_criteria}    ${search_type}=patient
    
    Navigate To Appointment Management
    
    # Select search type
    Select From Dropdown    css:select[data-testid="search-type"]    ${search_type}
    
    # Enter search criteria
    Input Text Safely    ${APPOINTMENT_SEARCH_FIELD}    ${search_criteria}
    Click Element Safely    css:button[data-testid="search-appointments"]
    
    # Wait for search results
    Wait For Page Load
    Wait For Element To Be Visible    ${APPOINTMENT_LIST}    ${WAIT_TIMEOUT}
    
    Log    Appointment search completed for: ${search_criteria}

View Appointment Details
    [Documentation]    Views detailed information for a specific appointment
    [Arguments]    ${appointment_id}
    
    # Search for the appointment
    Search For Appointment    ${appointment_id}    id
    
    # Select appointment from results
    ${appointment_row}=    Set Variable    css:[data-appointment-id="${appointment_id}"]
    Click Element Safely    ${appointment_row}
    
    # Wait for appointment details to load
    Wait For Element To Be Visible    ${APPOINTMENT_DETAILS_PANEL}    ${WAIT_TIMEOUT}
    
    # Verify all appointment information is displayed
    ${details_sections}=    Create List    
    ...    .appointment-info
    ...    .patient-info
    ...    .provider-info
    ...    .appointment-notes
    
    FOR    ${section}    IN    @{details_sections}
        ${section_visible}=    Run Keyword And Return Status
        ...    Wait For Element To Be Visible    css:${section}    ${SHORT_WAIT}
        IF    not ${section_visible}
            Log    Section ${section} not visible    level=WARN
        END
    END
    
    Log    Appointment details loaded for: ${appointment_id}

Reschedule Appointment
    [Documentation]    Reschedules an existing appointment to a new date/time
    [Arguments]    ${appointment_id}    ${new_date}    ${new_time}    ${reason}=${EMPTY}
    
    # View appointment details
    View Appointment Details    ${appointment_id}
    
    # Click reschedule button
    Click Element Safely    css:button[data-testid="reschedule-appointment"]
    Wait For Element To Be Visible    css:form[data-testid="reschedule-form"]    ${WAIT_TIMEOUT}
    
    # Set new date and time
    Input Text Safely    css:input[name="newDate"]    ${new_date}
    
    # Check availability for new time
    Click Element Safely    css:button[data-testid="check-new-availability"]
    Wait For Element To Be Visible    css:select[name="newTimeSlot"]    ${WAIT_TIMEOUT}
    
    # Select new time slot
    Select From Dropdown    css:select[name="newTimeSlot"]    ${new_time}
    
    # Add reschedule reason if provided
    IF    '${reason}' != '${EMPTY}'
        Input Text Safely    css:textarea[name="rescheduleReason"]    ${reason}
    END
    
    # Confirm reschedule
    Click Element Safely    css:button[data-testid="confirm-reschedule"]
    
    # Verify success
    Verify Success Message Displayed    Appointment rescheduled successfully
    
    Log    Appointment ${appointment_id} rescheduled to ${new_date} ${new_time}

Cancel Appointment
    [Documentation]    Cancels an appointment with reason
    [Arguments]    ${appointment_id}    ${cancellation_reason}    ${notify_patient}=True
    
    # View appointment details
    View Appointment Details    ${appointment_id}
    
    # Click cancel button
    Click Element Safely    ${CANCEL_APPOINTMENT_BUTTON}
    Wait For Element To Be Visible    css:form[data-testid="cancellation-form"]    ${WAIT_TIMEOUT}
    
    # Select cancellation reason
    Select From Dropdown    css:select[name="cancellationReason"]    ${cancellation_reason}
    
    # Set patient notification preference
    ${notify_checkbox}=    Set Variable    css:input[name="notifyPatient"]
    IF    ${notify_patient}
        Check Checkbox    ${notify_checkbox}
    ELSE
        Uncheck Checkbox    ${notify_checkbox}
    END
    
    # Add additional notes if needed
    Input Text Safely    css:textarea[name="cancellationNotes"]    
    ...    Appointment cancelled via automated test
    
    # Confirm cancellation
    Click Element Safely    css:button[data-testid="confirm-cancellation"]
    
    # Verify cancellation
    Verify Success Message Displayed    Appointment cancelled successfully
    
    # Verify appointment status is updated
    ${status_indicator}=    Set Variable    css:[data-testid="appointment-status"]
    Wait For Element To Be Visible    ${status_indicator}    ${SHORT_WAIT}
    ${status}=    Get Text    ${status_indicator}
    Should Be Equal As Strings    ${status}    CANCELLED
    
    Log    Appointment ${appointment_id} cancelled with reason: ${cancellation_reason}

Check Provider Availability
    [Documentation]    Checks provider availability for a specific date range
    [Arguments]    ${provider_id}    ${start_date}    ${end_date}
    
    Navigate To Appointment Management
    
    # Navigate to provider schedule view
    Click Element Safely    css:button[data-testid="provider-schedule"]
    Wait For Element To Be Visible    css:form[data-testid="availability-check"]    ${WAIT_TIMEOUT}
    
    # Select provider
    Select From Dropdown    css:select[name="providerId"]    ${provider_id}
    
    # Set date range
    Input Text Safely    css:input[name="startDate"]    ${start_date}
    Input Text Safely    css:input[name="endDate"]      ${end_date}
    
    # Check availability
    Click Element Safely    css:button[data-testid="check-availability"]
    
    # Wait for availability results
    Wait For Element To Be Visible    css:[data-testid="availability-results"]    ${WAIT_TIMEOUT}
    
    # Get available slots
    ${available_slots}=    Get Elements    css:.available-slot
    ${slot_count}=    Get Length    ${available_slots}
    
    Log    Provider ${provider_id} has ${slot_count} available slots from ${start_date} to ${end_date}
    [Return]    ${slot_count}

Block Provider Time
    [Documentation]    Blocks provider time for non-patient activities
    [Arguments]    ${provider_id}    ${block_date}    ${start_time}    ${end_time}    ${reason}
    
    Navigate To Appointment Management
    
    # Navigate to schedule blocking
    Click Element Safely    css:button[data-testid="block-time"]
    Wait For Element To Be Visible    css:form[data-testid="time-block-form"]    ${WAIT_TIMEOUT}
    
    # Select provider
    Select From Dropdown    css:select[name="providerId"]    ${provider_id}
    
    # Set block details
    Input Text Safely    css:input[name="blockDate"]    ${block_date}
    Input Text Safely    css:input[name="startTime"]    ${start_time}
    Input Text Safely    css:input[name="endTime"]      ${end_time}
    Input Text Safely    css:textarea[name="reason"]    ${reason}
    
    # Save time block
    Click Element Safely    css:button[data-testid="save-time-block"]
    
    # Verify success
    Verify Success Message Displayed    Time block created successfully
    
    Log    Provider ${provider_id} time blocked on ${block_date} from ${start_time} to ${end_time}

Generate Appointment Report
    [Documentation]    Generates appointment reports for specified criteria
    [Arguments]    ${report_type}    ${start_date}    ${end_date}    ${provider_id}=${EMPTY}
    
    Navigate To Appointment Management
    
    # Navigate to reports section
    Click Element Safely    css:button[data-testid="appointment-reports"]
    Wait For Element To Be Visible    css:form[data-testid="report-form"]    ${WAIT_TIMEOUT}
    
    # Select report type
    Select From Dropdown    css:select[name="reportType"]    ${report_type}
    
    # Set date range
    Input Text Safely    css:input[name="startDate"]    ${start_date}
    Input Text Safely    css:input[name="endDate"]      ${end_date}
    
    # Select provider if specified
    IF    '${provider_id}' != '${EMPTY}'
        Select From Dropdown    css:select[name="providerId"]    ${provider_id}
    END
    
    # Generate report
    Click Element Safely    css:button[data-testid="generate-report"]
    
    # Wait for report generation
    Wait For Element To Be Visible    css:[data-testid="report-results"]    ${WAIT_TIMEOUT}
    
    # Verify report contains data
    ${report_rows}=    Get Elements    css:.report-row
    ${row_count}=    Get Length    ${report_rows}
    Should Be True    ${row_count} > 0    Report should contain data
    
    Log    Appointment report generated: ${report_type} for ${start_date} to ${end_date}

Validate Appointment Data
    [Documentation]    Validates appointment data integrity
    [Arguments]    ${appointment_id}    &{expected_data}
    
    View Appointment Details    ${appointment_id}
    
    # Validate each expected field
    FOR    ${field}    ${expected_value}    IN    &{expected_data}
        ${field_locator}=    Set Variable    css:[data-field="${field}"]
        TRY
            ${actual_value}=    Get Text    ${field_locator}
            Should Contain    ${actual_value}    ${expected_value}
            Log    Field ${field} validation passed: ${expected_value}
        EXCEPT
            Log    Field ${field} validation failed or element not found    level=WARN
        END
    END
    
    Log    Appointment data validation completed for: ${appointment_id}

Check Appointment Reminder Status
    [Documentation]    Checks if appointment reminders are properly configured
    [Arguments]    ${appointment_id}
    
    View Appointment Details    ${appointment_id}
    
    # Check reminder settings
    ${reminder_section}=    Set Variable    css:[data-testid="reminder-settings"]
    Wait For Element To Be Visible    ${reminder_section}    ${WAIT_TIMEOUT}
    
    # Verify reminder types are configured
    ${reminder_types}=    Create List    email    sms    phone
    
    FOR    ${reminder_type}    IN    @{reminder_types}
        ${reminder_enabled}=    Run Keyword And Return Status
        ...    Wait For Element To Be Visible    css:input[name="${reminder_type}Reminder"]:checked    ${SHORT_WAIT}
        
        IF    ${reminder_enabled}
            Log    ${reminder_type} reminder is enabled for appointment ${appointment_id}
        ELSE
            Log    ${reminder_type} reminder is disabled for appointment ${appointment_id}
        END
    END