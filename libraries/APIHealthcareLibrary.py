"""
API Testing Library for Healthcare Applications
Provides comprehensive REST API testing capabilities with healthcare-specific validations
"""
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
import requests
from robot.api.deco import keyword  # type: ignore
from robot.libraries.BuiltIn import BuiltIn  # type: ignore


class APIHealthcareLibrary:
    """
    Custom API library for healthcare-specific API testing
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_AUTO_KEYWORDS = False

    def __init__(self):
        self.builtin = BuiltIn()
        self.session = requests.Session()
        self.base_url = ""
        self.auth_token = ""
        self.last_response = None
        
    @keyword("Set Healthcare API Base URL")
    def set_healthcare_api_base_url(self, url: str) -> None:
        """
        Sets the base URL for healthcare API endpoints
        
        Args:
            url: Base URL for the API
        """
        self.base_url = url.rstrip('/')
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'HealthcareTestFramework/1.0'
        })
        self.builtin.log(f"Healthcare API base URL set to: {self.base_url}")
    
    @keyword("Authenticate Healthcare API")
    def authenticate_healthcare_api(self, username: str, password: str,
                                   endpoint: str = "/auth/login") -> Optional[str]:
        """
        Authenticates with healthcare API and stores auth token
        
        Args:
            username: API username
            password: API password
            endpoint: Authentication endpoint
            
        Returns:
            Optional[Authentication token]
        """
        try:
            auth_data = {
                "username": username,
                "password": password
            }
            
            response = self.session.post(
                f"{self.base_url}{endpoint}",
                json=auth_data,
                timeout=30
            )
            
            response.raise_for_status()
            
            auth_response = response.json()
            self.auth_token = auth_response.get('token', auth_response.get('access_token', ''))
            
            if not self.auth_token:
                self.builtin.fail("Authentication token not found in response")
            
            # Set authorization header for subsequent requests
            self.session.headers.update({
                'Authorization': f'Bearer {self.auth_token}'
            })
            
            self.builtin.log("Healthcare API authentication successful")
            return self.auth_token
            
        except requests.exceptions.RequestException as e:
            self.builtin.fail(f"API authentication failed: {str(e)}")
            return None
    
    @keyword("GET Healthcare API")
    def get_healthcare_api(self, endpoint: str, params: Optional[Dict] = None,
                          expected_status: int = 200) -> Optional[Dict[str, Any]]:
        """
        Performs GET request to healthcare API endpoint
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            expected_status: Expected HTTP status code
            
        Returns:
            Optional[Response data as dictionary]
        """
        try:
            url = f"{self.base_url}{endpoint}"
            
            self.last_response = self.session.get(
                url,
                params=params,
                timeout=30
            )
            
            # Validate status code
            if self.last_response.status_code != expected_status:
                self.builtin.fail(
                    f"Expected status {expected_status}, got {self.last_response.status_code}"
                )
            
            # Parse and validate response
            response_data = self.last_response.json()
            
            self.builtin.log(f"GET {endpoint} - Status: {self.last_response.status_code}")
            return response_data
            
        except requests.exceptions.RequestException as e:
            self.builtin.fail(f"GET request failed for {endpoint}: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            self.builtin.fail(f"Invalid JSON response from {endpoint}: {str(e)}")
            return None
    
    @keyword("POST Healthcare API")
    def post_healthcare_api(self, endpoint: str, data: Dict[str, Any],
                           expected_status: int = 201) -> Optional[Dict[str, Any]]:
        """
        Performs POST request to healthcare API endpoint
        
        Args:
            endpoint: API endpoint path
            data: Request payload
            expected_status: Expected HTTP status code
            
        Returns:
            Optional[Response data as dictionary]
        """
        try:
            url = f"{self.base_url}{endpoint}"
            
            self.last_response = self.session.post(
                url,
                json=data,
                timeout=30
            )
            
            # Validate status code
            if self.last_response.status_code != expected_status:
                self.builtin.fail(
                    f"Expected status {expected_status}, got {self.last_response.status_code}"
                )
            
            # Parse response
            response_data = self.last_response.json()
            
            self.builtin.log(f"POST {endpoint} - Status: {self.last_response.status_code}")
            return response_data
            
        except requests.exceptions.RequestException as e:
            self.builtin.fail(f"POST request failed for {endpoint}: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            self.builtin.fail(f"Invalid JSON response from {endpoint}: {str(e)}")
            return None
    
    def _check_required_fields(self, response_data: Dict[str, Any], required_fields: List[str]) -> None:
        """Check for presence of required fields in response data."""
        missing_fields = []
        for field in required_fields:
            if field not in response_data or response_data[field] is None:
                missing_fields.append(field)

        if missing_fields:
            self.builtin.fail(f"Missing required fields in patient response: {missing_fields}")

    def _validate_field_types(self, response_data: Dict[str, Any]) -> None:
        """Validate data types for specific fields."""
        validations = {
            'patient_id': str,
            'first_name': str,
            'last_name': str,
            'date_of_birth': str,  # Should be ISO format
            'gender': str
        }

        for field, expected_type in validations.items():
            if field in response_data:
                if not isinstance(response_data[field], expected_type):
                    self.builtin.fail(
                        f"Field '{field}' should be {expected_type.__name__}, "
                        f"got {type(response_data[field]).__name__}"
                    )

    def _validate_date_of_birth(self, response_data: Dict[str, Any]) -> None:
        """Validate date_of_birth format."""
        if 'date_of_birth' in response_data:
            try:
                datetime.fromisoformat(response_data['date_of_birth'].replace('Z', '+00:00'))
            except ValueError:
                self.builtin.fail("Invalid date_of_birth format. Expected ISO format.")

    @keyword("Validate Patient API Response")
    def validate_patient_api_response(self, response_data: Dict[str, Any],
                                    required_fields: Optional[List[str]] = None) -> None:
        """
        Validates patient API response structure and data

        Args:
            response_data: API response to validate
            required_fields: List of required fields to check
        """
        try:
            # Default required fields for patient data
            if required_fields is None:
                required_fields = [
                    'patient_id', 'first_name', 'last_name',
                    'date_of_birth', 'gender'
                ]

            self._check_required_fields(response_data, required_fields)
            self._validate_field_types(response_data)
            self._validate_date_of_birth(response_data)

            self.builtin.log("Patient API response validation passed")

        except Exception as e:  # pylint: disable=broad-except
            self.builtin.fail(f"Patient API response validation failed: {str(e)}")
    
    @keyword("Validate FHIR Compliance")
    def validate_fhir_compliance(self, response_data: Dict[str, Any]) -> None:
        """
        Validates API response against FHIR standards
        
        Args:
            response_data: API response to validate
        """
        try:
            # Basic FHIR resource structure validation
            required_fhir_fields = ['resourceType', 'id']
            
            for field in required_fhir_fields:
                if field not in response_data:
                    self.builtin.fail(f"FHIR required field missing: {field}")
            
            # Validate resource type
            valid_resource_types = [
                'Patient', 'Practitioner', 'Encounter', 'Observation',
                'MedicationRequest', 'DiagnosticReport', 'Appointment'
            ]
            
            resource_type = response_data.get('resourceType')
            if resource_type not in valid_resource_types:
                self.builtin.fail(f"Invalid FHIR resourceType: {resource_type}")
            
            # Validate FHIR ID format
            fhir_id = response_data.get('id')
            if not isinstance(fhir_id, str) or len(fhir_id) == 0:
                self.builtin.fail("FHIR ID must be a non-empty string")
            
            self.builtin.log(f"FHIR compliance validated for {resource_type} resource")

        except Exception as e:  # pylint: disable=broad-except
            self.builtin.fail(f"FHIR compliance validation failed: {str(e)}")
    
    def _validate_single_security_header(self, header: str, expected_value, actual_value) -> Optional[str]:
        """
        Validates a single security header and returns error message if invalid, None if valid.

        Args:
            header: Header name
            expected_value: Expected value (None means just presence check)
            actual_value: Actual header value

        Returns:
            Error message or None
        """
        if actual_value is None:
            return f"Missing: {header}"
        if expected_value is not None:
            if isinstance(expected_value, list):
                if actual_value not in expected_value:
                    return f"Invalid {header}: {actual_value}"
            elif actual_value != expected_value:
                return f"Invalid {header}: {actual_value}"
        return None

    @keyword("Validate API Security Headers")
    def validate_api_security_headers(self) -> None:
        """
        Validates presence of required security headers in API response
        """
        try:
            if not self.last_response:
                self.builtin.fail("No response available for security header validation")

            required_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': None,  # Should be present
                'Content-Security-Policy': None     # Should be present
            }

            validation_errors = []

            for header, expected_value in required_headers.items():
                actual_value = self.last_response.headers.get(header)
                error = self._validate_single_security_header(header, expected_value, actual_value)
                if error:
                    validation_errors.append(error)

            # Report validation results
            if validation_errors:
                self.builtin.fail(f"Security header validation errors: {validation_errors}")

            self.builtin.log("API security headers validation passed")

        except Exception as e:  # pylint: disable=broad-except
            self.builtin.fail(f"Security headers validation failed: {str(e)}")
    
    @keyword("Validate API Rate Limiting")
    def validate_api_rate_limiting(self, endpoint: str, requests_count: int = 10,
                                   time_window: int = 60) -> None:
        """
        Tests API rate limiting functionality

        Args:
            endpoint: API endpoint to test
            requests_count: Number of requests to send
            time_window: Time window in seconds
        """
        try:
            url = f"{self.base_url}{endpoint}"
            responses = []
            delay = time_window / requests_count if requests_count > 0 else 0

            # Send requests spaced over the time window
            for i in range(requests_count):
                try:
                    response = self.session.get(url, timeout=10)
                    responses.append(response.status_code)
                except requests.exceptions.RequestException:
                    responses.append(0)  # Connection error
                if i < requests_count - 1:
                    time.sleep(delay)

            # Check for rate limiting responses (429 Too Many Requests)
            rate_limited = [status for status in responses if status == 429]

            if not rate_limited:
                self.builtin.log(
                    f"Warning: No rate limiting detected after {requests_count} requests over {time_window}s",
                    level="WARN"
                )
            else:
                self.builtin.log(
                    f"Rate limiting working correctly. "
                    f"{len(rate_limited)} requests were rate limited."
                )

        except Exception as e:  # pylint: disable=broad-except
            self.builtin.fail(f"Rate limiting validation failed: {str(e)}")
    
    @keyword("Clear Healthcare API Session")
    def clear_healthcare_api_session(self) -> None:
        """
        Clears API session and authentication data
        """
        try:
            self.session.close()
            self.session = requests.Session()
            self.auth_token = ""
            self.last_response = None
            
            self.builtin.log("Healthcare API session cleared successfully")

        except Exception as e:  # pylint: disable=broad-except
            self.builtin.log(f"Error clearing API session: {str(e)}", level="WARN")