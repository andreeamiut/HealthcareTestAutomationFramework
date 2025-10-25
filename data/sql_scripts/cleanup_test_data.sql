-- Test data cleanup script for healthcare test automation
-- Use this script to clean up test data after test execution

-- Disable foreign key checks temporarily (for MySQL)
-- SET foreign_key_checks = 0;

-- For PostgreSQL, delete in correct order to maintain referential integrity
BEGIN;

-- Clean up audit trail
DELETE FROM audit_trail WHERE patient_id LIKE 'TEST_%' OR patient_id LIKE 'PAT_%';

-- Clean up vital signs (cascade will handle this, but explicit for clarity)
DELETE FROM vital_signs WHERE record_id IN (
    SELECT record_id FROM medical_records WHERE patient_id LIKE 'TEST_%' OR patient_id LIKE 'PAT_%'
);

-- Clean up medical records
DELETE FROM medical_records WHERE patient_id LIKE 'TEST_%' OR patient_id LIKE 'PAT_%';

-- Clean up medications
DELETE FROM medications WHERE patient_id LIKE 'TEST_%' OR patient_id LIKE 'PAT_%';

-- Clean up allergies
DELETE FROM patient_allergies WHERE patient_id LIKE 'TEST_%' OR patient_id LIKE 'PAT_%';

-- Clean up appointments
DELETE FROM appointments WHERE patient_id LIKE 'TEST_%' OR patient_id LIKE 'PAT_%';

-- Clean up patients (this should cascade to related records)
DELETE FROM patients WHERE patient_id LIKE 'TEST_%' OR patient_id LIKE 'PAT_%';

-- Clean up test users (but keep the standard test users)
DELETE FROM users WHERE user_id LIKE 'TESTUSER_%';

-- Re-enable foreign key checks (for MySQL)
-- SET foreign_key_checks = 1;

COMMIT;

-- Verify cleanup
SELECT 'Patients' as table_name, COUNT(*) as remaining_test_records
FROM patients WHERE patient_id LIKE 'TEST_%' OR patient_id LIKE 'PAT_%'
UNION ALL
SELECT 'Appointments', COUNT(*) as remaining_test_records
FROM appointments WHERE patient_id LIKE 'TEST_%' OR patient_id LIKE 'PAT_%'
UNION ALL
SELECT 'Medical Records', COUNT(*) as remaining_test_records
FROM medical_records WHERE patient_id LIKE 'TEST_%' OR patient_id LIKE 'PAT_%'
UNION ALL
SELECT 'Medications', COUNT(*) as remaining_test_records
FROM medications WHERE patient_id LIKE 'TEST_%' OR patient_id LIKE 'PAT_%'
UNION ALL
SELECT 'Allergies', COUNT(*) as remaining_test_records
FROM patient_allergies WHERE patient_id LIKE 'TEST_%' OR patient_id LIKE 'PAT_%';
