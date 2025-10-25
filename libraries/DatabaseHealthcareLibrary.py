"""
Enhanced Database Library for Healthcare Test Automation
Provides comprehensive database testing capabilities for healthcare applications
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import sqlite3

try:
    from robot.api.deco import keyword
    from robot.libraries.BuiltIn import BuiltIn
    ROBOT_AVAILABLE = True
except ImportError:
    ROBOT_AVAILABLE = False
    def keyword(func):
        """Fallback keyword decorator when robot framework is not available."""
        return func

try:
    import psycopg2  # type: ignore
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

try:
    import pymysql  # type: ignore
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False


# Custom exceptions for healthcare database operations
class HealthcareDatabaseError(Exception):
    """Base exception for healthcare database operations"""


class DatabaseConnectionError(HealthcareDatabaseError):
    """Raised when database connection fails"""


class ValidationError(HealthcareDatabaseError):
    """Raised when data validation fails"""


class SecurityError(HealthcareDatabaseError):
    """Raised when security validation fails"""


class TestDataError(HealthcareDatabaseError):
    """Raised when test data operations fail"""


class DatabaseHealthcareLibrary:
    """
    Custom database library with healthcare-specific functionality
    """
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_AUTO_KEYWORDS = False
    
    def __init__(self):
        if ROBOT_AVAILABLE:
            self.builtin = BuiltIn()
        else:
            self.builtin = None
        self.connections = {}
        self.current_connection = None
        
    def _connect_postgresql(self, config: Dict[str, Any]) -> Any:
        """Connect to PostgreSQL database."""
        if not PSYCOPG2_AVAILABLE:
            raise DatabaseConnectionError("psycopg2 is not available. Please install psycopg2-binary.")
        return psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['username'],
            password=config['password'],
            sslmode='require'  # Enforce SSL for healthcare data
        )

    def _connect_mysql(self, config: Dict[str, Any]) -> Any:
        """Connect to MySQL database."""
        if not PYMYSQL_AVAILABLE:
            raise DatabaseConnectionError("pymysql is not available. Please install pymysql.")
        return pymysql.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['username'],
            password=config['password'],
            charset='utf8mb4',
            ssl={'ssl_disabled': False}  # Enforce SSL
        )

    def _connect_sqlite(self, config: Dict[str, Any]) -> Any:
        """Connect to SQLite database."""
        connection = sqlite3.connect(config['database'])
        connection.row_factory = sqlite3.Row
        return connection

    @keyword("Connect To Healthcare Database")
    def connect_to_healthcare_database(self, config: Dict[str, Any],
                                     alias: str = "default") -> None:
        """
        Establishes connection to healthcare database with proper security

        Args:
            config: Dictionary containing db_type, host, port, database, username, password
            alias: Connection alias for multiple databases
        """
        try:
            db_type = config.get('db_type', '').lower()
            if db_type == 'postgresql':
                connection = self._connect_postgresql(config)
            elif db_type == 'mysql':
                connection = self._connect_mysql(config)
            elif db_type == 'sqlite':
                connection = self._connect_sqlite(config)
            else:
                raise ValueError(f"Unsupported database type: {db_type}")

            self.connections[alias] = {
                'connection': connection,
                'type': db_type
            }
            self.current_connection = alias

            self.builtin.log(f"Connected to {db_type} database: {config['database']} as {alias}")

        except (psycopg2.Error if PSYCOPG2_AVAILABLE else Exception,
                pymysql.Error if PYMYSQL_AVAILABLE else Exception,
                sqlite3.Error) as db_error:
            if self.builtin:
                self.builtin.fail(f"Database connection failed: {str(db_error)}")
            else:
                raise DatabaseConnectionError(f"Database connection failed: {str(db_error)}") from db_error
        except (ValueError, KeyError) as config_error:
            if self.builtin:
                self.builtin.fail(f"Configuration error: {str(config_error)}")
            else:
                raise DatabaseConnectionError(f"Configuration error: {str(config_error)}") from config_error
    
    def _fetch_results(self, cursor, db_type: str) -> List[Dict]:
        """
        Fetches query results based on database type

        Args:
            cursor: Database cursor
            db_type: Type of database

        Returns:
            List of result dictionaries
        """
        if db_type == 'sqlite':
            # SQLite returns Row objects
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        else:
            # PostgreSQL/MySQL
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    def _validate_connection(self, alias: str) -> Dict[str, Any]:
        """Validate and return connection info."""
        if alias not in self.connections:
            error_msg = f"Database connection '{alias}' not found"
            if self.builtin:
                self.builtin.fail(error_msg)
            else:
                raise DatabaseConnectionError(error_msg)
        return self.connections[alias]

    def _execute_query_with_cursor(self, cursor, query: str, parameters: Optional[List]) -> None:
        """Execute query with optional parameters."""
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)

    def _handle_query_error(self, error: Exception, error_type: str) -> None:
        """Handle query execution errors."""
        error_msg = f"{error_type}: {str(error)}"
        if self.builtin:
            self.builtin.fail(error_msg)
        else:
            raise ValidationError(error_msg) from error

    @keyword("Execute Healthcare Query")
    def execute_healthcare_query(self, query: str, parameters: Optional[List] = None,
                                fetch: bool = True, alias: str = "default") -> List[Dict]:
        """
        Executes SQL query with healthcare-specific logging and auditing

        Args:
            query: SQL query to execute
            parameters: Query parameters for prepared statements
            fetch: Whether to fetch results
            alias: Database connection alias

        Returns:
            Query results as list of dictionaries
        """
        connection_info = self._validate_connection(alias)
        connection = connection_info['connection']
        db_type = connection_info['type']

        cursor = connection.cursor()
        try:
            # Log query execution (sanitized for security)
            sanitized_query = self._sanitize_query_for_logging(query)
            self.builtin.log(f"Executing query: {sanitized_query}")

            # Execute query
            self._execute_query_with_cursor(cursor, query, parameters)

            # Fetch results if requested
            results = self._fetch_results(cursor, db_type) if fetch else []

            connection.commit()

            self.builtin.log(f"Query executed successfully. Rows affected/returned: {len(results)}")
            return results

        except (psycopg2.Error if PSYCOPG2_AVAILABLE else Exception,
                pymysql.Error if PYMYSQL_AVAILABLE else Exception,
                sqlite3.Error) as db_error:
            self._handle_query_error(db_error, "Query execution failed")
            return []
        except TypeError as type_error:
            self._handle_query_error(type_error, "Invalid query parameters")
            return []
        finally:
            cursor.close()
    
    @keyword("Validate Patient Data Integrity")
    def validate_patient_data_integrity(self, patient_id: str, 
                                      alias: str = "default") -> Dict[str, bool]:
        """
        Validates patient data integrity across multiple tables
        
        Args:
            patient_id: Patient identifier
            alias: Database connection alias
            
        Returns:
            Dictionary of validation results
        """
        validation_results = {}
        
        try:
            # Check patient record exists
            patient_query = "SELECT COUNT(*) as count FROM patients WHERE patient_id = %s"
            result = self.execute_healthcare_query(patient_query, [patient_id], alias=alias)
            validation_results['patient_exists'] = result[0]['count'] > 0
            
            if not validation_results['patient_exists']:
                self.builtin.log(f"Patient {patient_id} not found in database", level="WARN")
                return validation_results
            
            # Validate required fields are not null
            required_fields_query = """
            SELECT 
                CASE WHEN first_name IS NOT NULL THEN 1 ELSE 0 END as has_first_name,
                CASE WHEN last_name IS NOT NULL THEN 1 ELSE 0 END as has_last_name,
                CASE WHEN date_of_birth IS NOT NULL THEN 1 ELSE 0 END as has_dob,
                CASE WHEN social_security_number IS NOT NULL THEN 1 ELSE 0 END as has_ssn
            FROM patients WHERE patient_id = %s
            """
            result = self.execute_healthcare_query(required_fields_query, [patient_id], alias=alias)
            
            if result:
                validation_results.update({
                    'has_required_fields': all(result[0].values()),
                    'field_details': result[0]
                })
            
            # Check for orphaned records
            orphan_checks = [
                ("appointments", "SELECT COUNT(*) as count FROM appointments WHERE patient_id = %s"),
                ("medical_records", "SELECT COUNT(*) as count FROM medical_records WHERE patient_id = %s"),
                ("prescriptions", "SELECT COUNT(*) as count FROM prescriptions WHERE patient_id = %s")
            ]
            
            for table_name, query in orphan_checks:
                result = self.execute_healthcare_query(query, [patient_id], alias=alias)
                validation_results[f'{table_name}_count'] = result[0]['count']
            
            # Overall integrity check
            validation_results['data_integrity_passed'] = (
                validation_results['patient_exists'] and
                validation_results.get('has_required_fields', False)
            )
            
            self.builtin.log(f"Patient data integrity validation completed for {patient_id}")
            return validation_results
            
        except (psycopg2.Error if PSYCOPG2_AVAILABLE else Exception,
                pymysql.Error if PYMYSQL_AVAILABLE else Exception,
                sqlite3.Error) as e:
            self.builtin.fail(f"Data integrity validation failed: {str(e)}")
        except (KeyError, IndexError, TypeError) as e:
            self.builtin.fail(f"Data integrity validation failed due to data structure error: {str(e)}")
    
    @keyword("Create Test Patient")
    def create_test_patient(self, patient_data: Dict[str, Any],
                           alias: str = "default") -> Optional[str]:
        """
        Creates a test patient with realistic healthcare data

        Args:
            patient_data: Patient information dictionary
            alias: Database connection alias

        Returns:
            Generated patient ID or None if creation failed
        """
        try:
            connection_info = self._validate_connection(alias)
            db_type = connection_info['type']

            # Generate patient ID if not provided
            if 'patient_id' not in patient_data:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                patient_data['patient_id'] = f"TEST_{timestamp}"

            # Set default values for required fields
            defaults = {
                'created_date': datetime.now(),
                'updated_date': datetime.now(),
                'status': 'ACTIVE',
                'created_by': 'TEST_AUTOMATION'
            }

            for key, value in defaults.items():
                if key not in patient_data:
                    patient_data[key] = value

            # Build insert query with database-specific placeholders
            columns = list(patient_data.keys())
            if db_type == 'sqlite':
                placeholders = ['?'] * len(columns)
            else:
                placeholders = ['%s'] * len(columns)
            values = list(patient_data.values())

            insert_query = f"""
            INSERT INTO patients ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            """

            self.execute_healthcare_query(insert_query, values, fetch=False, alias=alias)

            patient_id = patient_data['patient_id']
            self.builtin.log(f"Test patient created successfully: {patient_id}")

            return patient_id

        except (psycopg2.Error if PSYCOPG2_AVAILABLE else Exception,
                pymysql.Error if PYMYSQL_AVAILABLE else Exception,
                sqlite3.Error) as db_error:
            error_msg = f"Failed to create test patient: {str(db_error)}"
            if self.builtin:
                self.builtin.fail(error_msg)
            else:
                raise TestDataError(error_msg) from db_error
            return None
    
    @keyword("Cleanup Test Data")
    def cleanup_test_data(self, patient_ids: List[str], alias: str = "default") -> None:
        """
        Safely removes test data while maintaining referential integrity

        Args:
            patient_ids: List of patient IDs to clean up
            alias: Database connection alias
        """
        if not patient_ids:
            self._log_message("No patient IDs provided for cleanup")
            return

        connection_info = self._validate_connection(alias)
        db_type = connection_info['type']

        # Define cleanup order (child tables first)
        cleanup_tables = [
            "prescriptions",
            "medical_records",
            "appointments",
            "patient_allergies",
            "patient_medications",
            "patients"
        ]

        try:
            for table in cleanup_tables:
                # Delete records for all patient_ids at once
                self._delete_from_table(table, patient_ids, db_type, alias)

                # Count remaining records
                remaining_count = self._count_remaining(table, patient_ids, db_type, alias)
                if remaining_count == 0:
                    self._log_message(f"All test data cleaned from {table}")

            self._log_message(f"Test data cleanup completed for {len(patient_ids)} patients")

        except (psycopg2.Error if PSYCOPG2_AVAILABLE else Exception,
                pymysql.Error if PYMYSQL_AVAILABLE else Exception) as db_error:
            error_msg = f"Test data cleanup failed: {str(db_error)}"
            if ROBOT_AVAILABLE:
                self.builtin.fail(error_msg)
            else:
                raise TestDataError(error_msg) from db_error
    
    @keyword("Verify HIPAA Audit Trail")
    def verify_hipaa_audit_trail(self, patient_id: str, action: str,
                                user_id: str, alias: str = "default") -> bool:
        """
        Verifies HIPAA audit trail entries for patient data access
        
        Args:
            patient_id: Patient identifier
            action: Action performed (READ, UPDATE, DELETE, etc.)
            user_id: User who performed the action
            alias: Database connection alias
            
        Returns:
            True if audit trail entry exists
        """
        try:
            audit_query = """
            SELECT COUNT(*) as count 
            FROM audit_trail 
            WHERE patient_id = %s 
              AND action = %s 
              AND user_id = %s 
              AND created_date >= %s
            """
            
            # Check for entries in the last 5 minutes
            time_threshold = datetime.now() - timedelta(minutes=5)
            
            result = self.execute_healthcare_query(
                audit_query, 
                [patient_id, action, user_id, time_threshold], 
                alias=alias
            )
            
            audit_exists = result[0]['count'] > 0
            
            if audit_exists:
                self.builtin.log(f"HIPAA audit trail verified for {action} on patient {patient_id}")
            else:
                self.builtin.fail(f"HIPAA audit trail missing for {action} on patient {patient_id}")
            
            return audit_exists
            
        except (psycopg2.Error if PSYCOPG2_AVAILABLE else Exception,
                pymysql.Error if PYMYSQL_AVAILABLE else Exception) as db_error:
            if self.builtin:
                self.builtin.fail(f"HIPAA audit trail verification failed: {str(db_error)}")
            else:
                raise SecurityError(f"HIPAA audit trail verification failed: {str(db_error)}") from db_error
    
    def _sanitize_query_for_logging(self, query: str) -> str:
        """
        Sanitizes SQL query for safe logging (removes sensitive data patterns)

        Args:
            query: Original SQL query

        Returns:
            Sanitized query string
        """
        # Remove potential sensitive data patterns
        sensitive_patterns = [
            (r"ssn\s*=\s*'[^']+'", "ssn = '***'"),
            (r"social_security_number\s*=\s*'[^']+'", "social_security_number = '***'"),
            (r"password\s*=\s*'[^']+'", "password = '***'"),
            (r"token\s*=\s*'[^']+'", "token = '***'")
        ]

        sanitized = query
        for pattern, replacement in sensitive_patterns:
            import re
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        return sanitized

    def _log_message(self, message: str, level: str = "INFO") -> None:
        """Helper method for consistent logging."""
        if ROBOT_AVAILABLE:
            self.builtin.log(message, level=level)
        else:
            print(f"[{level}] {message}")

    def _get_placeholder(self, db_type: str, count: int) -> str:
        """Get database-specific placeholders."""
        if db_type == 'sqlite':
            return ', '.join(['?'] * count)
        else:
            return ', '.join(['%s'] * count)

    def _delete_from_table(self, table: str, patient_ids: List[str], db_type: str, alias: str) -> None:
        """Delete records from a table for given patient IDs."""
        if not patient_ids:
            return
        placeholders = self._get_placeholder(db_type, len(patient_ids))
        delete_query = f"DELETE FROM {table} WHERE patient_id IN ({placeholders})"
        self.execute_healthcare_query(delete_query, patient_ids, fetch=False, alias=alias)

    def _count_remaining(self, table: str, patient_ids: List[str], db_type: str, alias: str) -> int:
        """Count remaining records in table for given patient IDs."""
        if not patient_ids:
            return 0
        placeholders = self._get_placeholder(db_type, len(patient_ids))
        count_query = f"SELECT COUNT(*) as count FROM {table} WHERE patient_id IN ({placeholders})"
        result = self.execute_healthcare_query(count_query, patient_ids, alias=alias)
        return result[0]['count'] if result else 0
    
    @keyword("Disconnect From Healthcare Database")
    def disconnect_from_healthcare_database(self, alias: str = "default") -> None:
        """
        Safely disconnects from database with proper cleanup
        
        Args:
            alias: Database connection alias
        """
        try:
            if alias in self.connections:
                connection = self.connections[alias]['connection']
                connection.close()
                del self.connections[alias]
                
                if self.current_connection == alias:
                    self.current_connection = None
                
                self.builtin.log(f"Disconnected from database: {alias}")
            else:
                self.builtin.log(f"Database connection '{alias}' not found", level="WARN")
                
        except (psycopg2.Error if PSYCOPG2_AVAILABLE else Exception,
                pymysql.Error if PYMYSQL_AVAILABLE else Exception) as db_error:
            if self.builtin:
                self.builtin.log(f"Error during database disconnection: {str(db_error)}", level="WARN")
            else:
                # Log warning but don't raise exception for disconnection errors
                pass