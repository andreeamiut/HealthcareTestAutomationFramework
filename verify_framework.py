"""
Healthcare Test Automation Framework - Verification Script
Tests all major components to ensure framework is working correctly
"""
# pylint: disable=unused-import,redefined-outer-name

def test_imports():  # pylint: disable=import-outside-toplevel
    """Test that all required packages can be imported"""
    print("=" * 70)
    print("TEST 1: Verifying Package Imports")
    print("=" * 70)
    
    try:
        # Core testing frameworks
        import robot  # noqa: F401
        print("✓ Robot Framework imported successfully")
        
        from robot.api.deco import keyword  # noqa: F401
        from robot.libraries.BuiltIn import BuiltIn  # noqa: F401
        print("✓ Robot Framework decorators and libraries imported")
        
        # Web automation
        import playwright  # noqa: F401
        print("✓ Playwright imported successfully")
        
        import selenium  # noqa: F401
        print("✓ Selenium imported successfully")
        
        # Database
        import pymysql  # noqa: F401
        print("✓ PyMySQL imported successfully")
        
        # API testing
        import requests  # noqa: F401
        import jsonschema  # noqa: F401
        print("✓ Requests and JSON Schema imported successfully")
        
        # Utilities
        from cryptography.fernet import Fernet  # noqa: F401
        print("✓ Cryptography imported successfully")
        
        import faker  # noqa: F401
        print("✓ Faker imported successfully")
        
        # Testing frameworks
        import pytest  # noqa: F401 # pylint: disable=import-outside-toplevel
        print("✓ Pytest imported successfully")
        
        import allure  # noqa: F401
        print("✓ Allure imported successfully")
        
        print("\n✅ All package imports successful!\n")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import failed: {e}\n")
        return False


def test_custom_libraries():  # pylint: disable=import-outside-toplevel
    """Test that custom healthcare libraries can be imported"""
    print("=" * 70)
    print("TEST 2: Verifying Custom Healthcare Libraries")
    print("=" * 70)
    
    import os
    
    # Add libraries directory to path
    lib_path = os.path.join(os.path.dirname(__file__), 'libraries')
    import sys
    sys.path.insert(0, lib_path)
    
    try:
        from APIHealthcareLibrary import APIHealthcareLibrary  # type: ignore
        print("✓ APIHealthcareLibrary imported successfully")
        
        # Test instantiation
        api_lib = APIHealthcareLibrary()
        print(f"✓ APIHealthcareLibrary instantiated: {type(api_lib).__name__}")
        
        from DatabaseHealthcareLibrary import DatabaseHealthcareLibrary  # type: ignore
        print("✓ DatabaseHealthcareLibrary imported successfully")
        
        # Test instantiation
        db_lib = DatabaseHealthcareLibrary()
        print(f"✓ DatabaseHealthcareLibrary instantiated: {type(db_lib).__name__}")
        
        from PlaywrightHealthcareLibrary import PlaywrightHealthcareLibrary  # type: ignore
        print("✓ PlaywrightHealthcareLibrary imported successfully")
        
        # Test instantiation
        pw_lib = PlaywrightHealthcareLibrary()
        print(f"✓ PlaywrightHealthcareLibrary instantiated: {type(pw_lib).__name__}")
        
        print("\n✅ All custom libraries working!\n")
        return True
        
    except ImportError as e:
        print(f"\n❌ Library test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_helpers():  # pylint: disable=import-outside-toplevel
    """Test helper utilities"""
    print("=" * 70)
    print("TEST 3: Verifying Helper Utilities")
    print("=" * 70)
    
    import os
    
    # Add utils directory to path
    utils_path = os.path.join(os.path.dirname(__file__), 'utils')
    import sys
    sys.path.insert(0, utils_path)
    
    try:
        from helpers import DataFactory, TestDataManager, SecurityHelper  # type: ignore
        print("✓ Helper classes imported successfully")
        
        # Test DataFactory
        data_factory = DataFactory()
        patient_data = data_factory.generate_patient_data()
        print(f"✓ DataFactory created patient data: {patient_data['first_name']} {patient_data['last_name']}")
        
        # Test TestDataManager
        test_manager = TestDataManager()
        print(f"✓ TestDataManager instantiated: {type(test_manager).__name__}")
        
        # Test SecurityHelper
        security = SecurityHelper()
        encrypted = security.encrypt_sensitive_data("test_data")
        decrypted = security.decrypt_sensitive_data(encrypted)
        assert decrypted == "test_data"
        print("✓ SecurityHelper encryption/decryption working")
        
        print("\n✅ All helper utilities working!\n")
        return True
        
    except (ImportError, AssertionError) as e:
        print(f"\n❌ Utility test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_page_objects():  # pylint: disable=import-outside-toplevel
    """Test page object models"""
    print("=" * 70)
    print("TEST 4: Verifying Page Object Models")
    print("=" * 70)
    
    import os
    
    # Add page_objects directory to path
    pages_path = os.path.join(os.path.dirname(__file__), 'page_objects')
    import sys
    sys.path.insert(0, pages_path)
    
    try:
        from healthcare_pages import LoginPage, DashboardPage, PatientManagementPage  # type: ignore  # noqa: F401
        print("✓ Page object classes imported successfully")
        
        print(f"✓ LoginPage class available: {LoginPage.__name__}")
        print(f"✓ DashboardPage class available: {DashboardPage.__name__}")
        print(f"✓ PatientManagementPage class available: {PatientManagementPage.__name__}")
        
        print("\n✅ All page objects working!\n")
        return True
        
    except (ImportError, AttributeError) as e:
        print(f"\n❌ Page object test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_api_functionality():  # pylint: disable=import-outside-toplevel
    """Test basic API functionality"""
    print("=" * 70)
    print("TEST 5: Testing API Functionality")
    print("=" * 70)
    
    try:
        import requests
        
        # Test a simple public API to verify requests work
        response = requests.get('https://httpbin.org/get', timeout=10)
        print(f"✓ HTTP GET request successful (Status: {response.status_code})")
        
        # Test JSON response
        if response.status_code == 200:
            data = response.json()
            print(f"✓ JSON parsing successful (Keys: {list(data.keys())[:5]})")
        
        print("\n✅ API functionality working!\n")
        return True
        
    except (requests.RequestException, ValueError) as e:
        print(f"\n❌ API test failed: {e}\n")
        return False


def test_data_generation():  # pylint: disable=import-outside-toplevel
    """Test data generation capabilities"""
    print("=" * 70)
    print("TEST 6: Testing Data Generation")
    print("=" * 70)
    
    try:
        from faker import Faker
        
        fake = Faker()
        
        # Generate healthcare-related test data
        patient_name = fake.name()
        patient_email = fake.email()
        patient_phone = fake.phone_number()
        patient_address = fake.address()
        patient_dob = fake.date_of_birth(minimum_age=18, maximum_age=90)
        
        print(f"✓ Generated patient name: {patient_name}")
        print(f"✓ Generated email: {patient_email}")
        print(f"✓ Generated phone: {patient_phone}")
        print(f"✓ Generated DOB: {patient_dob}")
        print(f"✓ Generated address: {patient_address.replace(chr(10), ', ')}")
        
        print("\n✅ Data generation working!\n")
        return True
        
    except (ImportError, AttributeError) as e:
        print(f"\n❌ Data generation test failed: {e}\n")
        return False


def test_encryption():  # pylint: disable=import-outside-toplevel
    """Test encryption capabilities"""
    print("=" * 70)
    print("TEST 7: Testing Encryption")
    print("=" * 70)
    
    try:
        from cryptography.fernet import Fernet
        
        # Generate a key
        key = Fernet.generate_key()
        cipher = Fernet(key)
        
        # Test encryption/decryption
        sensitive_data = b"Patient SSN: 123-45-6789"
        encrypted = cipher.encrypt(sensitive_data)
        decrypted = cipher.decrypt(encrypted)
        
        assert decrypted == sensitive_data
        
        print(f"✓ Original data: {sensitive_data.decode()}")
        print(f"✓ Encrypted (truncated): {encrypted[:50]}...")
        print(f"✓ Decrypted successfully: {decrypted.decode()}")
        
        print("\n✅ Encryption working!\n")
        return True
        
    except (ImportError, AssertionError) as e:
        print(f"\n❌ Encryption test failed: {e}\n")
        return False


def test_robot_framework():  # pylint: disable=import-outside-toplevel
    """Test Robot Framework functionality"""
    print("=" * 70)
    print("TEST 8: Testing Robot Framework")
    print("=" * 70)
    
    try:
        from robot.api import TestSuite
        
        # Create a simple test suite
        suite = TestSuite('Healthcare Framework Test')
        
        # Robot Framework 7.x uses different API
        # suite.tests is a list, use append instead of create
        from robot.running.model import TestCase
        test = TestCase(name='Sample Test')
        test.body.create_keyword('Log', args=['Healthcare framework is working!'])
        suite.tests.append(test)
        
        print("✓ Test suite created successfully")
        print(f"✓ Test suite name: {suite.name}")
        print(f"✓ Number of tests: {len(suite.tests)}")
        
        print("\n✅ Robot Framework working!\n")
        return True
        
    except (ImportError, AttributeError) as e:
        print(f"\n❌ Robot Framework test failed: {e}\n")
        return False


def main():
    """Run all verification tests"""
    print("\n" + "=" * 70)
    print("HEALTHCARE TEST AUTOMATION FRAMEWORK - VERIFICATION")
    print("=" * 70 + "\n")
    
    results = []
    
    # Run all tests
    results.append(("Package Imports", test_imports()))
    results.append(("Custom Libraries", test_custom_libraries()))
    results.append(("Helper Utilities", test_helpers()))
    results.append(("Page Objects", test_page_objects()))
    results.append(("API Functionality", test_api_functionality()))
    results.append(("Data Generation", test_data_generation()))
    results.append(("Encryption", test_encryption()))
    results.append(("Robot Framework", test_robot_framework()))
    
    # Print summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
    
    print("=" * 70)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Your healthcare framework is fully operational!\n")
        print("You can now:")
        print("  1. Run Robot Framework tests: robot tests/robot/")
        print("  2. Run API tests: pytest tests/api/")
        print("  3. Run all tests: python run_tests.py")
        print()
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.\n")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
