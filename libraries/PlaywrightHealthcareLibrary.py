"""
Enhanced Playwright Library for Healthcare Test Automation
Extends Robot Framework's Playwright functionality with healthcare-specific methods
"""
import os
from datetime import datetime
from typing import Optional
from robot.api.deco import keyword  # type: ignore
from robot.libraries.BuiltIn import BuiltIn  # type: ignore
from Browser import Browser  # type: ignore


class PlaywrightHealthcareLibrary:
    """
    Custom Playwright library with healthcare-specific functionality
    """
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_AUTO_KEYWORDS = False
    
    def __init__(self):
        self.browser_lib = Browser()
        self.builtin = BuiltIn()
        self.screenshot_counter = 0
        self.current_page = None
        
    @keyword("Open Healthcare Application")
    def open_healthcare_application(self, url: str, browser: str = "chromium", 
                                  headless: bool = False) -> None:
        """
        Opens healthcare application with optimized settings
        
        Args:
            url: Application URL
            browser: Browser type (chromium, firefox, webkit)
            headless: Run in headless mode
        """
        try:
            # Configure browser with healthcare-specific settings
            self.browser_lib.new_browser(
                browser=browser,
                headless=headless,
                args=['--disable-web-security', '--disable-features=VizDisplayCompositor']
            )
            
            self.browser_lib.new_context(
                viewport={'width': 1920, 'height': 1080},
                ignore_https_errors=True,
                record_video_dir='results/videos' if not headless else None
            )

            self.current_page = self.browser_lib.new_page()
            self.browser_lib.go_to(url)
            
            # Wait for application to load
            self.browser_lib.wait_for_load_state('networkidle', timeout='30s')
            
            # Log successful navigation
            self.builtin.log(f"Successfully opened healthcare application: {url}")
            
        except (ValueError, TypeError, RuntimeError) as e:
            self.builtin.fail(f"Failed to open healthcare application: {str(e)}")
    
    @keyword("Secure Login")
    def secure_login(self, username: str, password: str, 
                    two_factor_code: Optional[str] = None) -> None:
        """
        Performs secure login with optional 2FA support
        
        Args:
            username: User login name
            password: User password
            two_factor_code: Optional 2FA code
        """
        try:
            # Enter credentials
            self.browser_lib.fill_text("input[name='username']", username)
            self.browser_lib.fill_text("input[name='password']", password)
            
            # Handle 2FA if provided
            if two_factor_code:
                self.browser_lib.fill_text("input[name='twoFactor']", two_factor_code)
            
            # Click login button
            self.browser_lib.click("button[type='submit']")
            
            # Wait for successful login (dashboard or home page)
            self.browser_lib.wait_for_selector("text=Dashboard", timeout='15s')
            
            self.builtin.log(f"Successfully logged in as: {username}")
            
        except (ValueError, TypeError, RuntimeError) as e:
            self.capture_screenshot_on_failure("login_failure")
            self.builtin.fail(f"Login failed for user {username}: {str(e)}")
    
    @keyword("Wait For Patient Data Load")
    def wait_for_patient_data_load(self, patient_id: str, timeout: str = "30s") -> None:
        """
        Waits for patient data to fully load
        
        Args:
            patient_id: Patient identifier
            timeout: Maximum wait time
        """
        try:
            # Wait for patient info container
            self.browser_lib.wait_for_selector(
                f"[data-patient-id='{patient_id}']", 
                timeout=timeout
            )
            
            # Wait for loading spinners to disappear
            self.browser_lib.wait_for_selector(
                ".loading-spinner", 
                state='detached', 
                timeout='10s'
            )
            
            # Ensure all patient sections are loaded
            patient_sections = [
                ".patient-demographics",
                ".patient-medical-history", 
                ".patient-medications",
                ".patient-allergies"
            ]
            
            for section in patient_sections:
                self.browser_lib.wait_for_selector(section, timeout='5s')
            
            self.builtin.log(f"Patient data loaded successfully for ID: {patient_id}")
            
        except (ValueError, TypeError, RuntimeError) as e:
            self.capture_screenshot_on_failure("patient_data_load_failure")
            self.builtin.fail(f"Failed to load patient data for {patient_id}: {str(e)}")
    
    @keyword("Validate HIPAA Compliance Elements")
    def validate_hipaa_compliance_elements(self) -> None:
        """
        Validates presence of HIPAA compliance elements on the page
        """
        try:
            compliance_elements = [
                "text=Privacy Notice",
                "text=Patient Rights",
                "[data-testid='audit-trail']",
                ".encryption-indicator"
            ]
            
            missing_elements = []
            
            for element in compliance_elements:
                try:
                    self.browser_lib.wait_for_selector(element, timeout='5s')
                except (ValueError, TypeError, RuntimeError):
                    missing_elements.append(element)
            
            if missing_elements:
                self.builtin.fail(f"HIPAA compliance elements missing: {missing_elements}")
            
            self.builtin.log("All HIPAA compliance elements validated successfully")
            
        except (ValueError, TypeError, RuntimeError) as e:
            self.capture_screenshot_on_failure("hipaa_validation_failure")
            self.builtin.fail(f"HIPAA compliance validation failed: {str(e)}")
    
    @keyword("Capture Screenshot On Failure")
    def capture_screenshot_on_failure(self, test_name: str) -> str:
        """
        Captures screenshot with timestamp for failure analysis
        
        Args:
            test_name: Name of the test for filename
            
        Returns:
            Screenshot file path
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.screenshot_counter += 1
            
            filename = f"{test_name}_{timestamp}_{self.screenshot_counter}.png"
            filepath = os.path.join("results", "screenshots", filename)
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            self.browser_lib.take_screenshot(filename=filepath)
            
            self.builtin.log(f"Screenshot captured: {filepath}")
            return filepath
            
        except (ValueError, TypeError, RuntimeError, OSError) as e:
            self.builtin.log(f"Failed to capture screenshot: {str(e)}", level="WARN")
            return ""
    
    @keyword("Verify Page Load Performance")
    def verify_page_load_performance(self, max_load_time: float = 3.0) -> None:
        """
        Verifies page load performance meets healthcare standards
        
        Args:
            max_load_time: Maximum acceptable load time in seconds
        """
        try:
            # Measure load time using Navigation Timing API
            load_time_script = """
            () => {
                const timing = performance.timing;
                return (timing.loadEventEnd - timing.navigationStart) / 1000;
            }
            """
            
            load_time = self.browser_lib.evaluate_javascript(load_time_script)
            
            if load_time > max_load_time:
                self.builtin.fail(
                    f"Page load time {load_time:.2f}s exceeds maximum {max_load_time}s"
                )
            
            self.builtin.log(f"Page load time: {load_time:.2f}s (within acceptable range)")
            
        except (ValueError, TypeError, RuntimeError) as e:
            self.builtin.log(f"Performance check failed: {str(e)}", level="WARN")
    
    @keyword("Close Healthcare Application")
    def close_healthcare_application(self) -> None:
        """
        Safely closes healthcare application with proper cleanup
        """
        try:
            # Clear any sensitive data from memory
            self.browser_lib.evaluate_javascript("sessionStorage.clear();")
            self.browser_lib.evaluate_javascript("localStorage.clear();")
            
            # Close browser
            self.browser_lib.close_browser()
            
            self.builtin.log("Healthcare application closed safely")
            
        except (ValueError, TypeError, RuntimeError) as e:
            self.builtin.log(f"Error during application closure: {str(e)}", level="WARN")