"""
API Tests for Healthcare Application
Tests REST API endpoints for patient management, appointments, and authentication
"""
import pytest
from libraries.APIHealthcareLibrary import APIHealthcareLibrary
from libraries.DatabaseHealthcareLibrary import DatabaseHealthcareLibrary
from utils.helpers import DataFactory, TestDataManager
import os
import time


class TestHealthcareAPI:
    """Test suite for Healthcare API endpoints"""

    def __init__(self):
        """Initialize test class attributes"""
        self.api = None
        self.db = None
        self.data_factory = None
        self.test_data_manager = None
        self.auth_token = None
        self.created_patients = []
        self.created_appointments = []

    @pytest.fixture(scope="class", autouse=True)
    def setup_api_tests(self):
        """Setup for API test suite"""
        self.api = APIHealthcareLibrary()
        self.db = DatabaseHealthcareLibrary()
        self.data_factory = DataFactory()
        self.test_data_manager = TestDataManager()
        
        # Set base URL from environment
        api_base_url = os.getenv('API_BASE_URL', 'https://dev-api-healthcare.example.com')
        self.api.set_healthcare_api_base_url(api_base_url)
        
        # Authenticate
        self.auth_token = self.api.authenticate_healthcare_api('api_test_user', 'Test123!')
        
        # Setup database connection
        config = {
            'db_type': 'postgresql',
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'healthcare_test'),
            'username': os.getenv('DB_USER', 'test_user'),
            'password': os.getenv('DB_PASSWORD', 'test_password')
        }
        self.db.connect_to_healthcare_database(config)
        
        # Track created resources for cleanup
        self.created_patients = []
        self.created_appointments = []
        
        yield
        
        # Cleanup
        if self.created_patients:
            self.db.cleanup_test_data(self.created_patients)
        self.api.clear_healthcare_api_session()
        self.db.disconnect_from_healthcare_database()
    
    @pytest.mark.smoke
    @pytest.mark.api
    def test_api_authentication(self):
        """Test API authentication endpoint"""
        # Clear current session
        self.api.clear_healthcare_api_session()
        
        # Test successful authentication
        token = self.api.authenticate_healthcare_api('api_test_user', 'Test123!')
        assert token, "Authentication should return a token"
        assert len(token) > 0, "Token should not be empty"
        
        # Test invalid credentials
        with pytest.raises(Exception):
            self.api.authenticate_healthcare_api('invalid_user', 'wrong_password')
    
    @pytest.mark.api
    @pytest.mark.patient
    def test_create_patient_via_api(self):
        """Test creating a patient through API"""
        # Generate test patient data
        patient_data = self.data_factory.generate_patient_data()
        
        # Remove generated patient_id to let API generate it
        patient_data.pop('patient_id', None)
        patient_data.pop('created_date', None)
        patient_data.pop('status', None)
        
        # Create patient via API
        response = self.api.post_healthcare_api('/patients', patient_data)
        
        # Validate response structure
        self.api.validate_patient_api_response(response)
        
        # Verify required fields
        assert 'patient_id' in response
        assert response['first_name'] == patient_data['first_name']
        assert response['last_name'] == patient_data['last_name']
        assert response['date_of_birth'] == patient_data['date_of_birth']
        
        # Track for cleanup
        patient_id = response['patient_id']
        self.created_patients.append(patient_id)
        
        # Verify patient was created in database
        db_validation = self.db.validate_patient_data_integrity(patient_id)
        assert db_validation['patient_exists'], "Patient should exist in database"
        assert db_validation['has_required_fields'], "Required fields should be present"
    
    @pytest.mark.api
    @pytest.mark.patient
    def test_get_patient_by_id(self):
        """Test retrieving patient by ID through API"""
        # Create a test patient first
        patient_data = self.data_factory.generate_patient_data()
        patient_data.pop('patient_id', None)
        patient_data.pop('created_date', None)
        patient_data.pop('status', None)
        
        create_response = self.api.post_healthcare_api('/patients', patient_data)
        patient_id = create_response['patient_id']
        self.created_patients.append(patient_id)
        
        # Retrieve patient by ID
        get_response = self.api.get_healthcare_api(f'/patients/{patient_id}')
        
        # Validate response
        self.api.validate_patient_api_response(get_response)
        
        # Verify data matches
        assert get_response['patient_id'] == patient_id
        assert get_response['first_name'] == patient_data['first_name']
        assert get_response['last_name'] == patient_data['last_name']
    
    @pytest.mark.api
    @pytest.mark.patient
    def test_update_patient_via_api(self):
        """Test updating patient information through API"""
        # Create a test patient
        patient_data = self.data_factory.generate_patient_data()
        patient_data.pop('patient_id', None)
        patient_data.pop('created_date', None)
        patient_data.pop('status', None)
        
        create_response = self.api.post_healthcare_api('/patients', patient_data)
        patient_id = create_response['patient_id']
        self.created_patients.append(patient_id)
        
        # Update patient data
        update_data = {
            'phone_number': '555-9999',
            'email': 'updated.email@test.com',
            'address_line1': '999 Updated Street'
        }
        
        # Perform update
        update_response = self.api.post_healthcare_api(
            f'/patients/{patient_id}', 
            update_data, 
            expected_status=200
        )
        
        # Verify update
        assert update_response['phone_number'] == update_data['phone_number']
        assert update_response['email'] == update_data['email']
        assert update_response['address_line1'] == update_data['address_line1']
        
        # Verify in database
        db_query = f"SELECT phone_number, email, address_line1 FROM patients WHERE patient_id = '{patient_id}'"
        db_result = self.db.execute_healthcare_query(db_query)
        
        assert db_result[0]['phone_number'] == update_data['phone_number']
        assert db_result[0]['email'] == update_data['email']
        assert db_result[0]['address_line1'] == update_data['address_line1']
    
    @pytest.mark.api
    @pytest.mark.patient
    def test_search_patients_via_api(self):
        """Test patient search functionality through API"""
        # Create multiple test patients
        test_patients = []
        for i in range(3):
            patient_data = self.data_factory.generate_patient_data(
                first_name=f"SearchTest{i}",
                last_name="APIPatient"
            )
            patient_data.pop('patient_id', None)
            patient_data.pop('created_date', None)
            patient_data.pop('status', None)
            
            response = self.api.post_healthcare_api('/patients', patient_data)
            test_patients.append(response['patient_id'])
            self.created_patients.append(response['patient_id'])
        
        # Search by last name
        search_response = self.api.get_healthcare_api('/patients/search', {
            'last_name': 'APIPatient'
        })
        
        # Verify search results
        assert 'patients' in search_response
        assert len(search_response['patients']) >= 3
        
        # Verify all test patients are in results
        result_ids = [p['patient_id'] for p in search_response['patients']]
        for patient_id in test_patients:
            assert patient_id in result_ids
    
    @pytest.mark.api
    @pytest.mark.appointment
    def test_create_appointment_via_api(self):
        """Test creating appointment through API"""
        # Create a test patient first
        patient_data = self.data_factory.generate_patient_data()
        patient_data.pop('patient_id', None)
        patient_data.pop('created_date', None)
        patient_data.pop('status', None)
        
        patient_response = self.api.post_healthcare_api('/patients', patient_data)
        patient_id = patient_response['patient_id']
        self.created_patients.append(patient_id)
        
        # Generate appointment data
        appointment_data = self.data_factory.generate_appointment_data(patient_id=patient_id)
        appointment_data.pop('appointment_id', None)
        appointment_data.pop('created_date', None)
        
        # Create appointment
        appointment_response = self.api.post_healthcare_api('/appointments', appointment_data)
        
        # Validate response
        assert 'appointment_id' in appointment_response
        assert appointment_response['patient_id'] == patient_id
        assert appointment_response['provider_id'] == appointment_data['provider_id']
        assert appointment_response['appointment_type'] == appointment_data['appointment_type']
        
        # Track for cleanup
        appointment_id = appointment_response['appointment_id']
        self.created_appointments.append(appointment_id)
    
    @pytest.mark.api
    @pytest.mark.appointment
    def test_get_appointments_by_patient(self):
        """Test retrieving appointments for a specific patient"""
        # Create test patient and appointment
        patient_data = self.data_factory.generate_patient_data()
        patient_data.pop('patient_id', None)
        patient_data.pop('created_date', None)
        patient_data.pop('status', None)
        
        patient_response = self.api.post_healthcare_api('/patients', patient_data)
        patient_id = patient_response['patient_id']
        self.created_patients.append(patient_id)
        
        # Create appointment
        appointment_data = self.data_factory.generate_appointment_data(patient_id=patient_id)
        appointment_data.pop('appointment_id', None)
        appointment_data.pop('created_date', None)
        
        appointment_response = self.api.post_healthcare_api('/appointments', appointment_data)
        appointment_id = appointment_response['appointment_id']
        self.created_appointments.append(appointment_id)
        
        # Get appointments for patient
        appointments_response = self.api.get_healthcare_api(f'/patients/{patient_id}/appointments')
        
        # Validate response
        assert 'appointments' in appointments_response
        assert len(appointments_response['appointments']) >= 1
        
        # Find our appointment in the results
        our_appointment = next(
            (apt for apt in appointments_response['appointments'] 
             if apt['appointment_id'] == appointment_id), 
            None
        )
        assert our_appointment is not None, "Created appointment should be in patient's appointments"
    
    @pytest.mark.api
    @pytest.mark.fhir
    def test_fhir_compliance(self):
        """Test FHIR compliance of API responses"""
        # Create test patient
        patient_data = self.data_factory.generate_patient_data()
        patient_data.pop('patient_id', None)
        patient_data.pop('created_date', None)
        patient_data.pop('status', None)
        
        # Get FHIR-formatted response
        fhir_response = self.api.get_healthcare_api('/fhir/Patient', {
            'format': 'json'
        })
        
        # Validate FHIR compliance
        self.api.validate_fhir_compliance(fhir_response)
    
    @pytest.mark.api
    @pytest.mark.security
    def test_api_security_headers(self):
        """Test API security headers"""
        # Make any API call
        self.api.get_healthcare_api('/patients/search', {'last_name': 'Test'})
        
        # Validate security headers
        self.api.validate_api_security_headers()
    
    @pytest.mark.api
    @pytest.mark.security
    def test_api_rate_limiting(self):
        """Test API rate limiting functionality"""
        # Test rate limiting on search endpoint
        self.api.validate_api_rate_limiting('/patients/search', requests_count=15, time_window=60)
    
    @pytest.mark.api
    @pytest.mark.security
    def test_unauthorized_access(self):
        """Test API behavior with unauthorized access"""
        # Clear authentication
        self.api.clear_healthcare_api_session()
        
        # Attempt to access protected endpoint
        with pytest.raises(Exception):
            self.api.get_healthcare_api('/patients')
        
        # Re-authenticate for other tests
        self.api.authenticate_healthcare_api('api_test_user', 'Test123!')
    
    @pytest.mark.api
    @pytest.mark.patient
    def test_patient_data_validation(self):
        """Test API data validation for patient creation"""
        # Test with missing required fields
        invalid_patient_data = {
            'first_name': 'Test'
            # Missing last_name, date_of_birth, etc.
        }
        
        with pytest.raises(Exception):
            self.api.post_healthcare_api('/patients', invalid_patient_data)
        
        # Test with invalid date format
        invalid_date_patient = {
            'first_name': 'Test',
            'last_name': 'Patient',
            'date_of_birth': 'invalid-date',
            'gender': 'M'
        }
        
        with pytest.raises(Exception):
            self.api.post_healthcare_api('/patients', invalid_date_patient)
    
    @pytest.mark.api
    @pytest.mark.performance
    def test_api_response_time(self):
        """Test API response time performance"""
        
        # Test patient search performance
        start_time = time.time()
        self.api.get_healthcare_api('/patients/search', {'last_name': 'Test'})
        response_time = time.time() - start_time
        
        # API should respond within 2 seconds
        assert response_time < 2.0, f"API response time {response_time:.2f}s exceeds 2s threshold"
        
        # Test patient creation performance
        patient_data = self.data_factory.generate_patient_data()
        patient_data.pop('patient_id', None)
        patient_data.pop('created_date', None)
        patient_data.pop('status', None)
        
        start_time = time.time()
        response = self.api.post_healthcare_api('/patients', patient_data)
        response_time = time.time() - start_time
        
        # Track for cleanup
        self.created_patients.append(response['patient_id'])
        
        # Patient creation should complete within 3 seconds
        assert response_time < 3.0, f"Patient creation time {response_time:.2f}s exceeds 3s threshold"


if __name__ == "__main__":
    pytest.main(["-v", "--tb=short", "--html=results/api_test_report.html", __file__])