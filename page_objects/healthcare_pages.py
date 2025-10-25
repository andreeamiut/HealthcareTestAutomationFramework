"""
Page Object Model for Healthcare Application Login Page
"""
from typing import Optional
from playwright.sync_api import Page, expect


class LoginPage:
    """Page object for the healthcare application login page"""
    
    def __init__(self, page: Page):
        self.page = page
        
        # Locators
        self.username_field = page.locator("input[name='username']")
        self.password_field = page.locator("input[name='password']") 
        self.two_factor_field = page.locator("input[name='twoFactor']")
        self.login_button = page.locator("button[type='submit']")
        self.forgot_password_link = page.locator("a[href*='forgot-password']")
        self.error_message = page.locator(".error-message")
        self.remember_me_checkbox = page.locator("input[name='rememberMe']")
        self.role_selector = page.locator("select[name='role']")
        
    def navigate_to_login(self, url: str) -> None:
        """Navigate to the login page"""
        self.page.goto(url)
        expect(self.username_field).to_be_visible()
        
    def login(self, username: str, password: str, 
              two_factor_code: Optional[str] = None,
              remember_me: bool = False) -> None:
        """Perform login with credentials"""
        self.username_field.fill(username)
        self.password_field.fill(password)
        
        if two_factor_code:
            expect(self.two_factor_field).to_be_visible()
            self.two_factor_field.fill(two_factor_code)
            
        if remember_me:
            self.remember_me_checkbox.check()
            
        self.login_button.click()
        
    def get_error_message(self) -> str:
        """Get the error message text"""
        expect(self.error_message).to_be_visible()
        return self.error_message.text_content()
        
    def click_forgot_password(self) -> None:
        """Click the forgot password link"""
        self.forgot_password_link.click()
        
    def is_login_form_visible(self) -> bool:
        """Check if login form is visible"""
        return self.username_field.is_visible()


class DashboardPage:
    """Page object for the healthcare application dashboard"""
    
    def __init__(self, page: Page):
        self.page = page
        
        # Locators
        self.dashboard_container = page.locator("[data-testid='dashboard']")
        self.user_menu = page.locator("[data-testid='user-menu']")
        self.logout_button = page.locator("[data-testid='logout-button']")
        self.navigation_menu = page.locator(".navigation-menu")
        self.patients_menu = page.locator("a[href*='patients']")
        self.appointments_menu = page.locator("a[href*='appointments']") 
        self.reports_menu = page.locator("a[href*='reports']")
        self.admin_menu = page.locator("a[href*='admin']")
        self.user_role_display = page.locator("[data-testid='user-role']")
        
    def wait_for_dashboard_load(self) -> None:
        """Wait for dashboard to fully load"""
        expect(self.dashboard_container).to_be_visible()
        self.page.wait_for_load_state('networkidle')
        
    def navigate_to_patients(self) -> None:
        """Navigate to patients section"""
        self.patients_menu.click()
        
    def navigate_to_appointments(self) -> None:
        """Navigate to appointments section"""
        self.appointments_menu.click()
        
    def navigate_to_reports(self) -> None:
        """Navigate to reports section"""
        self.reports_menu.click()
        
    def navigate_to_admin(self) -> None:
        """Navigate to admin section"""
        expect(self.admin_menu).to_be_visible()
        self.admin_menu.click()
        
    def get_user_role(self) -> str:
        """Get the current user's role"""
        return self.user_role_display.text_content()
        
    def logout(self) -> None:
        """Perform logout"""
        self.user_menu.click()
        self.logout_button.click()
        
    def is_dashboard_loaded(self) -> bool:
        """Check if dashboard is loaded"""
        return self.dashboard_container.is_visible()


class PatientManagementPage:
    """Page object for patient management functionality"""
    
    def __init__(self, page: Page):
        self.page = page
        
        # Locators
        self.patient_search_field = page.locator("input[data-testid='patient-search']")
        self.search_button = page.locator("button[data-testid='search-patients']")
        self.new_patient_button = page.locator("button[data-testid='new-patient']")
        self.patient_list = page.locator("[data-testid='patient-list']")
        self.patient_form = page.locator("form[data-testid='patient-form']")
        self.save_button = page.locator("button[data-testid='save-patient']")
        self.patient_details_panel = page.locator("[data-testid='patient-details']")
        
        # Form fields
        self.first_name_field = page.locator("input[name='firstName']")
        self.last_name_field = page.locator("input[name='lastName']")
        self.date_of_birth_field = page.locator("input[name='dateOfBirth']")
        self.gender_selector = page.locator("select[name='gender']")
        self.phone_field = page.locator("input[name='phoneNumber']")
        self.email_field = page.locator("input[name='email']")
        
    def search_patient(self, search_term: str) -> None:
        """Search for a patient"""
        self.patient_search_field.fill(search_term)
        self.search_button.click()
        expect(self.patient_list).to_be_visible()
        
    def click_new_patient(self) -> None:
        """Click new patient button"""
        self.new_patient_button.click()
        expect(self.patient_form).to_be_visible()
        
    def fill_patient_form(self, patient_data: dict) -> None:
        """Fill the patient form with data"""
        if 'first_name' in patient_data:
            self.first_name_field.fill(patient_data['first_name'])
        if 'last_name' in patient_data:
            self.last_name_field.fill(patient_data['last_name'])
        if 'date_of_birth' in patient_data:
            self.date_of_birth_field.fill(patient_data['date_of_birth'])
        if 'gender' in patient_data:
            self.gender_selector.select_option(patient_data['gender'])
        if 'phone_number' in patient_data:
            self.phone_field.fill(patient_data['phone_number'])
        if 'email' in patient_data:
            self.email_field.fill(patient_data['email'])
            
    def save_patient(self) -> None:
        """Save the patient form"""
        self.save_button.click()
        
    def select_patient_from_list(self, patient_id: str) -> None:
        """Select a patient from the list"""
        patient_row = self.page.locator(f"[data-patient-id='{patient_id}']")
        patient_row.click()
        expect(self.patient_details_panel).to_be_visible()


class AppointmentManagementPage:
    """Page object for appointment management functionality"""
    
    def __init__(self, page: Page):
        self.page = page
        
        # Locators
        self.appointment_calendar = page.locator("[data-testid='appointment-calendar']")
        self.new_appointment_button = page.locator("button[data-testid='new-appointment']")
        self.appointment_form = page.locator("form[data-testid='appointment-form']")
        self.patient_lookup = page.locator("input[data-testid='patient-lookup']")
        self.provider_selector = page.locator("select[data-testid='provider']")
        self.appointment_type_selector = page.locator("select[data-testid='appointment-type']")
        self.date_picker = page.locator("input[name='appointmentDate']")
        self.time_slot_selector = page.locator("select[data-testid='time-slot']")
        self.save_appointment_button = page.locator("button[data-testid='save-appointment']")
        self.appointment_list = page.locator("[data-testid='appointment-list']")
        
    def wait_for_calendar_load(self) -> None:
        """Wait for appointment calendar to load"""
        expect(self.appointment_calendar).to_be_visible()
        
    def click_new_appointment(self) -> None:
        """Click new appointment button"""
        self.new_appointment_button.click()
        expect(self.appointment_form).to_be_visible()
        
    def search_patient(self, patient_id: str) -> None:
        """Search for patient in appointment form"""
        self.patient_lookup.fill(patient_id)
        search_button = self.page.locator("button[data-testid='search-patient']")
        search_button.click()
        
    def fill_appointment_form(self, appointment_data: dict) -> None:
        """Fill appointment form with data"""
        if 'provider_id' in appointment_data:
            self.provider_selector.select_option(appointment_data['provider_id'])
        if 'appointment_type' in appointment_data:
            self.appointment_type_selector.select_option(appointment_data['appointment_type'])
        if 'appointment_date' in appointment_data:
            self.date_picker.fill(appointment_data['appointment_date'])
        if 'time_slot' in appointment_data:
            # Check availability first
            check_availability_button = self.page.locator("button[data-testid='check-availability']")
            check_availability_button.click()
            expect(self.time_slot_selector).to_be_visible()
            self.time_slot_selector.select_option(appointment_data['time_slot'])
            
    def save_appointment(self) -> None:
        """Save the appointment"""
        self.save_appointment_button.click()
        
    def get_appointment_id(self) -> str:
        """Get the generated appointment ID"""
        appointment_id_element = self.page.locator("[data-testid='appointment-id']")
        expect(appointment_id_element).to_be_visible()
        return appointment_id_element.text_content()