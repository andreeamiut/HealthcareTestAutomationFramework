"""
Unit tests for APIHealthcareLibrary class
Tests API library functionality for healthcare test automation
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from libraries.APIHealthcareLibrary import APIHealthcareLibrary


class TestAPIHealthcareLibrary:
    """Test suite for APIHealthcareLibrary class"""

    def setup_method(self):
        """Setup for each test method"""
        self.api = APIHealthcareLibrary()

    def test_initialization(self):
        """Test library initialization"""
        assert self.api.base_url == ""
        assert self.api.auth_token == ""
        assert self.api.last_response is None
        assert hasattr(self.api, 'session')
        assert isinstance(self.api.session, requests.Session)

    @patch('requests.Session.post')
    def test_authenticate_healthcare_api_success(self, mock_post):
        """Test successful API authentication"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {"token": "test_token_123"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        token = self.api.authenticate_healthcare_api("test_user", "test_pass")

        assert token == "test_token_123"
        assert self.api.auth_token == "test_token_123"
        mock_post.assert_called_once()

        # Check that Authorization header was set
        assert self.api.session.headers.get('Authorization') == 'Bearer test_token_123'

    @patch('requests.Session.post')
    def test_authenticate_healthcare_api_failure(self, mock_post):
        """Test failed API authentication"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
        mock_post.return_value = mock_response

        with pytest.raises(AssertionError):  # BuiltIn.fail() raises AssertionError
            self.api.authenticate_healthcare_api("wrong_user", "wrong_pass")

    @patch('requests.Session.get')
    def test_get_healthcare_api_success(self, mock_get):
        """Test successful GET request"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response

        self.api.base_url = "https://api.test.com"
        result = self.api.get_healthcare_api("/test/endpoint")

        assert result == {"data": "test"}
        assert self.api.last_response == mock_response
        mock_get.assert_called_once_with(
            "https://api.test.com/test/endpoint",
            params=None,
            timeout=30
        )

    @patch('requests.Session.get')
    def test_get_healthcare_api_wrong_status(self, mock_get):
        """Test GET request with unexpected status code"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        self.api.base_url = "https://api.test.com"

        with pytest.raises(AssertionError):  # BuiltIn.fail() raises AssertionError
            self.api.get_healthcare_api("/test/endpoint", expected_status=200)

    @patch('requests.Session.post')
    def test_post_healthcare_api_success(self, mock_post):
        """Test successful POST request"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 123, "name": "test"}
        mock_post.return_value = mock_response

        self.api.base_url = "https://api.test.com"
        data = {"name": "test_data"}
        result = self.api.post_healthcare_api("/test/endpoint", data)

        assert result == {"id": 123, "name": "test"}
        mock_post.assert_called_once_with(
            "https://api.test.com/test/endpoint",
            json=data,
            timeout=30
        )

    def test_set_healthcare_api_base_url(self):
        """Test setting base URL"""
        url = "https://api.healthcare.test"
        self.api.set_healthcare_api_base_url(url)

        assert self.api.base_url == url
        assert self.api.session.headers['Content-Type'] == 'application/json'
        assert self.api.session.headers['Accept'] == 'application/json'

    def test_validate_patient_api_response_success(self):
        """Test successful patient response validation"""
        response_data = {
            "patient_id": "PAT001",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01T00:00:00",
            "gender": "M"
        }

        # Should not raise exception
        self.api.validate_patient_api_response(response_data)

    def test_validate_patient_api_response_missing_field(self):
        """Test patient response validation with missing required field"""
        response_data = {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01T00:00:00",
            "gender": "M"
            # Missing patient_id
        }

        with pytest.raises(AssertionError):  # BuiltIn.fail() raises AssertionError
            self.api.validate_patient_api_response(response_data)

    def test_validate_patient_api_response_invalid_date(self):
        """Test patient response validation with invalid date format"""
        response_data = {
            "patient_id": "PAT001",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "invalid-date",
            "gender": "M"
        }

        with pytest.raises(AssertionError):  # BuiltIn.fail() raises AssertionError
            self.api.validate_patient_api_response(response_data)

    @patch('requests.Session.get')
    def test_validate_api_security_headers_success(self, mock_get):
        """Test successful security headers validation"""
        # Setup mock response with proper headers
        mock_response = Mock()
        mock_response.headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000',
            'Content-Security-Policy': "default-src 'self'"
        }

        self.api.last_response = mock_response

        # Should not raise exception
        self.api.validate_api_security_headers()

    @patch('requests.Session.get')
    def test_validate_api_security_headers_missing(self, mock_get):
        """Test security headers validation with missing headers"""
        mock_response = Mock()
        mock_response.headers = {}  # No security headers

        self.api.last_response = mock_response

        with pytest.raises(AssertionError):  # BuiltIn.fail() raises AssertionError
            self.api.validate_api_security_headers()

    @patch('time.sleep')
    @patch('requests.Session.get')
    def test_validate_api_rate_limiting(self, mock_get, mock_sleep):
        """Test rate limiting validation"""
        # Mock responses - some successful, some rate limited
        responses = []
        for i in range(10):
            mock_resp = Mock()
            mock_resp.status_code = 429 if i >= 7 else 200  # Rate limit after 7 requests
            responses.append(mock_resp)

        mock_get.side_effect = responses

        self.api.base_url = "https://api.test.com"

        # Should not raise exception - rate limiting is expected behavior
        self.api.validate_api_rate_limiting("/test/endpoint", requests_count=10)

    def test_validate_fhir_compliance_success(self):
        """Test successful FHIR compliance validation"""
        fhir_response = {
            "resourceType": "Patient",
            "id": "12345",
            "name": [{"family": "Doe", "given": ["John"]}]
        }

        # Should not raise exception
        self.api.validate_fhir_compliance(fhir_response)

    def test_validate_fhir_compliance_missing_resource_type(self):
        """Test FHIR compliance validation with missing resource type"""
        fhir_response = {
            "id": "12345",
            "name": [{"family": "Doe", "given": ["John"]}]
            # Missing resourceType
        }

        with pytest.raises(AssertionError):  # BuiltIn.fail() raises AssertionError
            self.api.validate_fhir_compliance(fhir_response)

    def test_validate_fhir_compliance_invalid_resource_type(self):
        """Test FHIR compliance validation with invalid resource type"""
        fhir_response = {
            "resourceType": "InvalidResource",
            "id": "12345"
        }

        with pytest.raises(AssertionError):  # BuiltIn.fail() raises AssertionError
            self.api.validate_fhir_compliance(fhir_response)

    def test_clear_healthcare_api_session(self):
        """Test clearing API session"""
        # Setup some state
        self.api.base_url = "https://api.test.com"
        self.api.auth_token = "test_token"
        self.api.last_response = Mock()

        self.api.clear_healthcare_api_session()

        assert self.api.base_url == "https://api.test.com"  # Should preserve base_url
        assert self.api.auth_token == ""
        assert self.api.last_response is None
        # Session should be recreated
        assert isinstance(self.api.session, requests.Session)