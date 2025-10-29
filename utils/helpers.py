"""
Utility classes and functions for Healthcare Test Automation Framework
"""
import os
import json
import csv
import yaml
import logging
from datetime import datetime
from typing import Dict, Any, List
from faker import Faker
from cryptography.fernet import Fernet


class ConfigManager:
    """Manages configuration loading and environment variables"""
    
    def __init__(self):
        self.config = {}
        self.environment = os.getenv('ENVIRONMENT', 'dev')
        
    def load_config(self, config_file: str = None) -> Dict[str, Any]:
        """Load configuration from file or environment variables"""
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.endswith('.json'):
                    self.config = json.load(f)
                elif config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    self.config = yaml.safe_load(f)
        
        # Override with environment variables
        env_vars = {
            'base_url': os.getenv('BASE_URL'),
            'api_base_url': os.getenv('API_BASE_URL'),
            'db_host': os.getenv('DB_HOST'),
            'db_port': os.getenv('DB_PORT'),
            'db_name': os.getenv('DB_NAME'),
            'timeout': os.getenv('TIMEOUT', '30'),
            'headless': os.getenv('HEADLESS', 'false').lower() == 'true'
        }
        
        for key, value in env_vars.items():
            if value is not None:
                self.config[key] = value
                
        return self.config


class DataFactory:
    """Generates realistic healthcare test data"""
    
    def __init__(self, locale: str = 'en_US'):
        self.fake = Faker(locale)
        Faker.seed(42)  # For reproducible test data
        
    def generate_patient_data(self, **overrides) -> Dict[str, Any]:
        """Generate realistic patient data"""
        gender = self.fake.random_element(['M', 'F', 'O'])
        
        if gender == 'M':
            first_name = self.fake.first_name_male()
        elif gender == 'F':
            first_name = self.fake.first_name_female()
        else:
            first_name = self.fake.first_name()
            
        patient_data = {
            'patient_id': f"PAT_{self.fake.random_number(digits=8, fix_len=True)}",
            'first_name': first_name,
            'last_name': self.fake.last_name(),
            'middle_name': self.fake.first_name(),
            'date_of_birth': self.fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat(),
            'gender': gender,
            'social_security_number': self.fake.ssn(),
            'phone_number': self.fake.phone_number(),
            'email': self.fake.email(),
            'address_line1': self.fake.street_address(),
            'address_line2': self.fake.secondary_address(),
            'city': self.fake.city(),
            'state': self.fake.state_abbr(),
            'zip_code': self.fake.zipcode(),
            'emergency_contact_name': self.fake.name(),
            'emergency_contact_phone': self.fake.phone_number(),
            'insurance_provider': self.fake.company(),
            'insurance_policy_number': f"INS{self.fake.random_number(digits=10, fix_len=True)}",
            'created_date': datetime.now().isoformat(),
            'status': 'ACTIVE'
        }
        
        # Apply any overrides
        patient_data.update(overrides)
        return patient_data
    
    def generate_appointment_data(self, patient_id: str = None, **overrides) -> Dict[str, Any]:
        """Generate realistic appointment data"""
        appointment_data = {
            'appointment_id': f"APT_{self.fake.random_number(digits=8, fix_len=True)}",
            'patient_id': patient_id or f"PAT_{self.fake.random_number(digits=8, fix_len=True)}",
            'provider_id': f"PRV_{self.fake.random_number(digits=6, fix_len=True)}",
            'appointment_type': self.fake.random_element([
                'CONSULTATION', 'FOLLOW_UP', 'ROUTINE_CHECKUP', 
                'PROCEDURE', 'EMERGENCY', 'TELEMEDICINE'
            ]),
            'appointment_date': self.fake.future_datetime(end_date='+30d').isoformat(),
            'duration_minutes': self.fake.random_element([15, 30, 45, 60, 90]),
            'status': self.fake.random_element(['SCHEDULED', 'CONFIRMED', 'IN_PROGRESS', 'COMPLETED']),
            'notes': self.fake.text(max_nb_chars=200),
            'created_date': datetime.now().isoformat()
        }
        
        appointment_data.update(overrides)
        return appointment_data
    
    def generate_medical_record_data(self, patient_id: str = None, **overrides) -> Dict[str, Any]:
        """Generate realistic medical record data"""
        medical_conditions = [
            'Hypertension', 'Diabetes Type 2', 'Asthma', 'COPD', 
            'Arthritis', 'Depression', 'Anxiety', 'Migraine'
        ]
        
        medications = [
            'Lisinopril', 'Metformin', 'Albuterol', 'Atorvastatin',
            'Omeprazole', 'Ibuprofen', 'Acetaminophen', 'Aspirin'
        ]
        
        record_data = {
            'record_id': f"MR_{self.fake.random_number(digits=10, fix_len=True)}",
            'patient_id': patient_id or f"PAT_{self.fake.random_number(digits=8, fix_len=True)}",
            'visit_date': self.fake.date_between(start_date='-2y', end_date='today').isoformat(),
            'chief_complaint': self.fake.text(max_nb_chars=100),
            'diagnosis': self.fake.random_element(medical_conditions),
            'treatment': self.fake.text(max_nb_chars=150),
            'medications': self.fake.random_elements(medications, length=self.fake.random_int(1, 3)),
            'vital_signs': {
                'blood_pressure_systolic': self.fake.random_int(90, 180),
                'blood_pressure_diastolic': self.fake.random_int(60, 110),
                'heart_rate': self.fake.random_int(60, 100),
                'temperature': round(self.fake.random.uniform(97.0, 101.0), 1),
                'weight_lbs': self.fake.random_int(100, 300),
                'height_inches': self.fake.random_int(60, 78)
            },
            'provider_notes': self.fake.text(max_nb_chars=300),
            'created_date': datetime.now().isoformat()
        }
        
        record_data.update(overrides)
        return record_data


class TestDataManager:
    """Manages test data files and operations"""
    
    def __init__(self, data_directory: str = "data/test_data"):
        self.data_dir = data_directory
        os.makedirs(data_directory, exist_ok=True)
        
    def save_test_data(self, data: List[Dict], filename: str, file_format: str = 'json') -> str:
        """Save test data to file"""
        filepath = os.path.join(self.data_dir, f"{filename}.{file_format}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if file_format == 'json':
                json.dump(data, f, indent=2)
            elif file_format == 'csv':
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            elif file_format in ['yaml', 'yml']:
                yaml.dump(data, f, default_flow_style=False)
        
        return filepath
    
    def load_test_data(self, filename: str) -> List[Dict]:
        """Load test data from file"""
        # Try different extensions
        for ext in ['json', 'csv', 'yaml', 'yml']:
            filepath = os.path.join(self.data_dir, f"{filename}.{ext}")
            if os.path.exists(filepath):
                return self._load_file(filepath, ext)
        
        raise FileNotFoundError(f"Test data file not found: {filename}")
    
    def _load_file(self, filepath: str, file_format: str) -> List[Dict]:
        """Load file based on format"""
        with open(filepath, 'r', encoding='utf-8') as f:
            if file_format == 'json':
                return json.load(f)
            elif file_format == 'csv':
                return list(csv.DictReader(f))
            elif file_format in ['yaml', 'yml']:
                return yaml.safe_load(f)


class SecurityHelper:
    """Security utilities for healthcare data"""

    def __init__(self, encryption_key: str = None):
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode())
        else:
            # Generate a key for the session
            self.cipher = Fernet(Fernet.generate_key())

    def generate_secure_password(self, length: int = 12) -> str:
        """Generate a secure password with required complexity"""
        import secrets
        import string

        if length < 8:
            length = 8

        # Define character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = '!@#$%^&*'

        # Ensure at least one character from each set
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(special)
        ]

        # Fill the rest randomly
        all_chars = lowercase + uppercase + digits + special
        password.extend(secrets.choice(all_chars) for _ in range(length - 4))

        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        return ''.join(password)

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        import bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        import bcrypt
        return bcrypt.checkpw(password.encode(), hashed.encode())

    def generate_api_key(self) -> str:
        """Generate a secure API key"""
        import secrets
        import base64

        # Generate 32 random bytes and encode as base64
        random_bytes = secrets.token_bytes(32)
        return base64.urlsafe_b64encode(random_bytes).decode().rstrip('=')

    def generate_jwt_token(self, payload: Dict[str, Any], secret: str) -> str:
        """Generate a JWT token"""
        import jwt
        import datetime

        # Add expiration time
        payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        payload['iat'] = datetime.datetime.utcnow()

        return jwt.encode(payload, secret, algorithm='HS256')

    def verify_jwt_token(self, token: str, secret: str) -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        import jwt

        return jwt.decode(token, secret, algorithms=['HS256'])

    def encrypt_data(self, data: str, key: str = None) -> str:
        """Encrypt data using Fernet"""
        if key:
            cipher = Fernet(key.encode())
        else:
            cipher = self.cipher
        return cipher.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data: str, key: str = None) -> str:
        """Decrypt data using Fernet"""
        if key:
            cipher = Fernet(key.encode())
        else:
            cipher = self.cipher
        return cipher.decrypt(encrypted_data.encode()).decode()

    def generate_encryption_key(self) -> str:
        """Generate a new encryption key"""
        return Fernet.generate_key().decode()

    def sanitize_input(self, input_str: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        import re
        # Remove potentially dangerous patterns
        sanitized = re.sub(r'<[^>]*>', '', input_str)  # Remove HTML tags
        sanitized = re.sub(r'(\b(union|select|insert|delete|update|drop|create|alter)\b)', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'(--|#|/\*|\*/)', '', sanitized)  # Remove SQL comments
        return sanitized.strip()

    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def validate_phone_number(self, phone: str) -> bool:
        """Validate phone number format"""
        import re
        # Allow various phone number formats
        pattern = r'^[\+]?[1-9][\d]{0,15}$|^[\(]?[\d]{3}[\)]?[\s-]?[\d]{3}[\s-]?[\d]{4}$'
        return bool(re.match(pattern, phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')))

    def generate_otp(self) -> str:
        """Generate a 6-digit OTP"""
        import secrets
        return ''.join(secrets.choice('0123456789') for _ in range(6))

    def verify_otp(self, otp: str, expected_otp: str, timestamp: float = None) -> bool:
        """Verify OTP with optional expiration check"""
        if timestamp:
            import time
            # OTP expires after 5 minutes
            if time.time() - timestamp > 300:
                return False
        return otp == expected_otp

    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive healthcare data"""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive healthcare data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

    def mask_pii(self, data: Dict[str, Any], fields_to_mask: List[str] = None) -> Dict[str, Any]:
        """Mask PII fields in data for logging"""
        if fields_to_mask is None:
            fields_to_mask = [
                'social_security_number', 'ssn', 'phone_number',
                'email', 'address_line1', 'address_line2'
            ]

        masked_data = data.copy()
        for field in fields_to_mask:
            if field in masked_data:
                value = str(masked_data[field])
                if len(value) > 4:
                    masked_data[field] = '*' * (len(value) - 4) + value[-4:]
                else:
                    masked_data[field] = '*' * len(value)

        return masked_data


class Logger:
    """Enhanced logging for healthcare test automation"""
    
    def __init__(self, name: str = 'HealthcareTestFramework'):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.INFO)
        
        if not self._logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # File handler
            os.makedirs('results/logs', exist_ok=True)
            file_handler = logging.FileHandler(
                f'results/logs/healthcare_tests_{datetime.now().strftime("%Y%m%d")}.log'
            )
            file_handler.setLevel(logging.DEBUG)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            self._logger.addHandler(console_handler)
            self._logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with optional context"""
        context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        full_message = f"{message} | {context}" if context else message
        self._logger.info(full_message)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message with optional context"""
        context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        full_message = f"{message} | {context}" if context else message
        self._logger.error(full_message)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with optional context"""
        context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        full_message = f"{message} | {context}" if context else message
        self._logger.debug(full_message)