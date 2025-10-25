"""
Simple API Tests for Healthcare Framework Verification
"""
import pytest


@pytest.mark.smoke
@pytest.mark.api
def test_import_api_library():
    """Test that API library can be imported"""
    from libraries.APIHealthcareLibrary import APIHealthcareLibrary
    api_lib = APIHealthcareLibrary()
    assert api_lib is not None
    assert hasattr(api_lib, 'set_healthcare_api_base_url')


@pytest.mark.api
def test_import_database_library():
    """Test that Database library can be imported"""
    from libraries.DatabaseHealthcareLibrary import DatabaseHealthcareLibrary
    db_lib = DatabaseHealthcareLibrary()
    assert db_lib is not None
    assert hasattr(db_lib, 'connect_to_healthcare_database')


@pytest.mark.api
def test_import_playwright_library():
    """Test that Playwright library can be imported"""
    from libraries.PlaywrightHealthcareLibrary import PlaywrightHealthcareLibrary
    pw_lib = PlaywrightHealthcareLibrary()
    assert pw_lib is not None
    assert hasattr(pw_lib, 'secure_login')


@pytest.mark.api
def test_data_factory():
    """Test data factory generates patient data"""
    from utils.helpers import DataFactory
    factory = DataFactory()
    patient_data = factory.generate_patient_data()
    
    assert 'first_name' in patient_data
    assert 'last_name' in patient_data
    assert 'email' in patient_data
    assert 'phone_number' in patient_data
    assert len(patient_data['first_name']) > 0


@pytest.mark.security
def test_security_helper():
    """Test security helper encryption"""
    from utils.helpers import SecurityHelper
    
    security = SecurityHelper()
    test_data = "Patient SSN: 123-45-6789"
    
    # Encrypt
    encrypted = security.encrypt_sensitive_data(test_data)
    assert encrypted != test_data
    assert len(encrypted) > len(test_data)
    
    # Decrypt
    decrypted = security.decrypt_sensitive_data(encrypted)
    assert decrypted == test_data


@pytest.mark.api
def test_requests_library():
    """Test that requests library works"""
    import requests
    
    response = requests.get('https://httpbin.org/get', timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert 'url' in data


@pytest.mark.smoke
def test_framework_version():
    """Test framework components are available"""
    import robot
    import requests
    
    assert robot is not None
    assert requests is not None
    assert pytest is not None
