"""
Unit tests for DataFactory utility class
Tests data generation functionality for healthcare test automation
"""
import pytest
from utils.helpers import DataFactory
from datetime import datetime, date


class TestDataFactory:
    """Test suite for DataFactory class"""

    def setup_method(self):
        """Setup for each test method"""
        self.factory = DataFactory()

    def test_generate_patient_data_basic(self):
        """Test basic patient data generation"""
        patient = self.factory.generate_patient_data()

        # Check required fields exist
        required_fields = ['patient_id', 'first_name', 'last_name', 'date_of_birth', 'gender']
        for field in required_fields:
            assert field in patient
            assert patient[field] is not None

        # Check data types
        assert isinstance(patient['patient_id'], str)
        assert isinstance(patient['first_name'], str)
        assert isinstance(patient['last_name'], str)
        assert isinstance(patient['date_of_birth'], str)
        assert patient['gender'] in ['M', 'F', 'O']

    def test_generate_patient_data_with_custom_values(self):
        """Test patient data generation with custom values"""
        custom_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'gender': 'M'
        }

        patient = self.factory.generate_patient_data(**custom_data)

        assert patient['first_name'] == 'John'
        assert patient['last_name'] == 'Doe'
        assert patient['gender'] == 'M'

    def test_generate_appointment_data(self):
        """Test appointment data generation"""
        patient_id = 'PAT001'
        appointment = self.factory.generate_appointment_data(patient_id=patient_id)

        # Check required fields
        required_fields = ['appointment_id', 'patient_id', 'provider_id',
                          'appointment_type', 'appointment_date']
        for field in required_fields:
            assert field in appointment
            assert appointment[field] is not None

        # Check patient_id is set correctly
        assert appointment['patient_id'] == patient_id

        # Check data types
        assert isinstance(appointment['appointment_id'], str)
        assert isinstance(appointment['appointment_date'], str)

    def test_generate_appointment_data_with_provider(self):
        """Test appointment data generation with specific provider"""
        patient_id = 'PAT001'
        provider_id = 'PRV001'

        appointment = self.factory.generate_appointment_data(
            patient_id=patient_id,
            provider_id=provider_id
        )

        assert appointment['patient_id'] == patient_id
        assert appointment['provider_id'] == provider_id

    def test_date_of_birth_format(self):
        """Test that date_of_birth is in correct ISO format"""
        patient = self.factory.generate_patient_data()

        # Should be able to parse as date
        dob_str = patient['date_of_birth']
        datetime.fromisoformat(dob_str.replace('Z', '+00:00'))

    def test_patient_id_format(self):
        """Test patient ID format"""
        patient = self.factory.generate_patient_data()

        # Should start with PAT and be followed by underscore and digits
        patient_id = patient['patient_id']
        assert patient_id.startswith('PAT_')
        assert patient_id[4:].isdigit()
        assert len(patient_id) >= 7  # PAT_ + at least 3 digits

    def test_appointment_id_format(self):
        """Test appointment ID format"""
        appointment = self.factory.generate_appointment_data()

        # Should start with APT and be followed by underscore and digits
        appointment_id = appointment['appointment_id']
        assert appointment_id.startswith('APT_')
        assert appointment_id[4:].isdigit()
        assert len(appointment_id) >= 7  # APT_ + at least 3 digits

    def test_appointment_types(self):
        """Test that appointment types are valid"""
        valid_types = [
            'CONSULTATION', 'FOLLOW_UP', 'ROUTINE_CHECKUP',
            'PROCEDURE', 'EMERGENCY', 'TELEMEDICINE'
        ]

        # Generate multiple appointments to test variety
        for _ in range(10):
            appointment = self.factory.generate_appointment_data()
            assert appointment['appointment_type'] in valid_types

    def test_provider_ids(self):
        """Test that provider IDs are valid"""
        # Provider IDs are generated with PRV_ prefix and random digits
        # We just verify the format is correct
        appointment = self.factory.generate_appointment_data()

        provider_id = appointment['provider_id']
        assert provider_id.startswith('PRV_')
        assert provider_id[4:].isdigit()
        assert len(provider_id) >= 7  # PRV_ + at least 3 digits

    def test_phone_number_format(self):
        """Test phone number format"""
        patient = self.factory.generate_patient_data()

        if 'phone_number' in patient and patient['phone_number']:
            phone = patient['phone_number']
            # Should be in format: XXX-XXX-XXXX or similar
            assert len(phone.replace('-', '').replace('(', '').replace(')', '')) >= 10

    def test_email_format(self):
        """Test email format"""
        patient = self.factory.generate_patient_data()

        if 'email' in patient and patient['email']:
            email = patient['email']
            # Basic email validation
            assert '@' in email
            assert '.' in email.split('@')[1]