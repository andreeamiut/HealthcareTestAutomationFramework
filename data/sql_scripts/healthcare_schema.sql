-- Healthcare Database Schema for Test Environment
-- This script creates the necessary tables for healthcare test automation

-- Patients table
CREATE TABLE IF NOT EXISTS patients (
    patient_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('M', 'F', 'O')),
    social_security_number VARCHAR(11),
    phone_number VARCHAR(15),
    email VARCHAR(100),
    address_line1 VARCHAR(100),
    address_line2 VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(15),
    insurance_provider VARCHAR(100),
    insurance_policy_number VARCHAR(50),
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE', 'DECEASED')),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) DEFAULT 'SYSTEM'
);

-- Providers table
CREATE TABLE IF NOT EXISTS providers (
    provider_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    specialty VARCHAR(100),
    license_number VARCHAR(50),
    phone_number VARCHAR(15),
    email VARCHAR(100),
    department VARCHAR(100),
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE')),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Appointments table
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id VARCHAR(20) PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    provider_id VARCHAR(20) NOT NULL,
    appointment_type VARCHAR(50) NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    status VARCHAR(20) DEFAULT 'SCHEDULED' CHECK (status IN ('SCHEDULED', 'CONFIRMED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'NO_SHOW')),
    notes TEXT,
    cancellation_reason VARCHAR(200),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (provider_id) REFERENCES providers(provider_id)
);

-- Medical Records table
CREATE TABLE IF NOT EXISTS medical_records (
    record_id VARCHAR(20) PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    provider_id VARCHAR(20),
    visit_date DATE NOT NULL,
    chief_complaint TEXT,
    diagnosis TEXT,
    treatment TEXT,
    provider_notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (provider_id) REFERENCES providers(provider_id)
);

-- Vital Signs table
CREATE TABLE IF NOT EXISTS vital_signs (
    vital_id SERIAL PRIMARY KEY,
    record_id VARCHAR(20) NOT NULL,
    blood_pressure_systolic INTEGER,
    blood_pressure_diastolic INTEGER,
    heart_rate INTEGER,
    temperature DECIMAL(4,1),
    weight_lbs INTEGER,
    height_inches INTEGER,
    recorded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (record_id) REFERENCES medical_records(record_id) ON DELETE CASCADE
);

-- Medications table
CREATE TABLE IF NOT EXISTS medications (
    medication_id SERIAL PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    medication_name VARCHAR(100) NOT NULL,
    dosage VARCHAR(50),
    frequency VARCHAR(50),
    start_date DATE,
    end_date DATE,
    prescribed_by VARCHAR(20),
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'DISCONTINUED', 'COMPLETED')),
    notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (prescribed_by) REFERENCES providers(provider_id)
);

-- Allergies table
CREATE TABLE IF NOT EXISTS patient_allergies (
    allergy_id SERIAL PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    allergen VARCHAR(100) NOT NULL,
    reaction VARCHAR(200),
    severity VARCHAR(20) CHECK (severity IN ('MILD', 'MODERATE', 'SEVERE')),
    discovered_date DATE,
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'RESOLVED')),
    notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- Audit Trail table for HIPAA compliance
CREATE TABLE IF NOT EXISTS audit_trail (
    audit_id SERIAL PRIMARY KEY,
    patient_id VARCHAR(20),
    user_id VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(50),
    record_id VARCHAR(50),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE SET NULL
);

-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(20) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('ADMIN', 'DOCTOR', 'NURSE', 'RECEPTIONIST', 'TECHNICIAN')),
    provider_id VARCHAR(20),
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE', 'LOCKED')),
    last_login TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    password_changed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (provider_id) REFERENCES providers(provider_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_patients_last_name ON patients(last_name);
CREATE INDEX IF NOT EXISTS idx_patients_dob ON patients(date_of_birth);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_provider ON appointments(provider_id);
CREATE INDEX IF NOT EXISTS idx_medical_records_patient ON medical_records(patient_id);
CREATE INDEX IF NOT EXISTS idx_medical_records_date ON medical_records(visit_date);
CREATE INDEX IF NOT EXISTS idx_audit_trail_patient ON audit_trail(patient_id);
CREATE INDEX IF NOT EXISTS idx_audit_trail_date ON audit_trail(created_date);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Insert sample test providers
INSERT INTO providers (provider_id, first_name, last_name, specialty, license_number, phone_number, email, department) VALUES
('PRV001', 'John', 'Smith', 'Internal Medicine', 'MD123456', '555-0101', 'j.smith@healthcare.test', 'Primary Care'),
('PRV002', 'Sarah', 'Johnson', 'Cardiology', 'MD234567', '555-0102', 's.johnson@healthcare.test', 'Cardiology'),
('PRV003', 'Michael', 'Brown', 'Pediatrics', 'MD345678', '555-0103', 'm.brown@healthcare.test', 'Pediatrics'),
('PRV004', 'Emily', 'Davis', 'Psychiatry', 'MD456789', '555-0104', 'e.davis@healthcare.test', 'Mental Health'),
('PRV005', 'Robert', 'Wilson', 'Emergency Medicine', 'MD567890', '555-0105', 'r.wilson@healthcare.test', 'Emergency')
ON CONFLICT (provider_id) DO NOTHING;

-- Insert sample test users
INSERT INTO users (user_id, username, email, password_hash, first_name, last_name, role, provider_id) VALUES
('USR001', 'admin_test', 'admin@healthcare.test', '$2b$12$dummy_hash_admin', 'Admin', 'User', 'ADMIN', NULL),
('USR002', 'doctor_test', 'doctor@healthcare.test', '$2b$12$dummy_hash_doctor', 'Doctor', 'Test', 'DOCTOR', 'PRV001'),
('USR003', 'nurse_test', 'nurse@healthcare.test', '$2b$12$dummy_hash_nurse', 'Nurse', 'Test', 'NURSE', NULL),
('USR004', 'receptionist_test', 'receptionist@healthcare.test', '$2b$12$dummy_hash_receptionist', 'Receptionist', 'Test', 'RECEPTIONIST', NULL)
ON CONFLICT (user_id) DO NOTHING;