# Healthcare Test Automation Framework

A comprehensive test automation framework for healthcare applications built with Python, Playwright, Robot Framework, and SQL.

## 🏥 Overview

This framework is designed specifically for healthcare applications, providing:
- **HIPAA-compliant testing** with audit trails and data privacy
- **Multi-layer testing** (UI, API, Database)
- **Role-based access control testing**
- **Patient data management testing**
- **Appointment scheduling testing**
- **Security and compliance validation**

## 🏗️ Architecture

```
healthCare/
├── config/                 # Environment configurations
├── data/                   # Test data and SQL scripts
│   ├── test_data/         # JSON/CSV test data files
│   └── sql_scripts/       # Database schemas and cleanup scripts
├── keywords/              # Robot Framework keywords
├── libraries/             # Custom Python libraries
├── page_objects/          # Page Object Model implementations
├── resources/             # Locators and static resources
├── results/               # Test execution results
├── tests/                 # Test suites
│   ├── ui/               # UI tests (Robot Framework)
│   ├── api/              # API tests (pytest)
│   └── database/         # Database tests
└── utils/                # Utility classes and helpers
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+ (for Playwright)
- PostgreSQL/MySQL (for database tests)
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd healthCare
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install
   ```

4. **Setup environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database:**
   ```bash
   psql -h localhost -U test_user -d healthcare_test -f data/sql_scripts/healthcare_schema.sql
   ```

## 🎯 Running Tests

### Using the Test Runner Script

```bash
# Run all tests
python run_tests.py all

# Run specific test types
python run_tests.py ui --browser chromium --headless
python run_tests.py api --environment staging
python run_tests.py smoke --environment dev

# Run with coverage
python run_tests.py unit --coverage

# Run in parallel
python run_tests.py ui --parallel

# Generate Allure report
python run_tests.py all --allure
```

### Direct Commands

**UI Tests (Robot Framework):**
```bash
robot --outputdir results tests/ui/
robot --include smoke tests/ui/
robot --variable ENVIRONMENT:staging tests/ui/
```

**API Tests (pytest):**
```bash
pytest tests/api/ -v --html=results/api-report.html
pytest -m smoke tests/api/
```

**Database Tests:**
```bash
robot --include database tests/database/
```

## 🧪 Test Categories

### Authentication Tests
- Login/logout functionality
- Two-factor authentication
- Role-based access control
- Session management
- Password policies
- Account lockout

### Patient Management Tests
- Patient creation and updates
- Patient search and retrieval
- Medical history management
- Medication tracking
- Allergy management
- Data integrity validation

### Appointment Tests
- Appointment scheduling
- Provider availability
- Appointment modifications
- Conflict resolution
- Reminder systems

### API Tests
- REST endpoint validation
- FHIR compliance
- Security headers
- Rate limiting
- Data validation

### Database Tests
- Data integrity
- HIPAA audit trails
- Performance
- Backup/recovery

## 🔧 Configuration

### Environment Files

**`.env` - Main configuration:**
```env
ENVIRONMENT=dev
BASE_URL=https://dev-healthcare.example.com
API_BASE_URL=https://dev-api-healthcare.example.com
DB_HOST=localhost
DB_PORT=5432
DB_NAME=healthcare_test
HEADLESS=false
BROWSER=chromium
```

**`config/environments.robot` - Robot Framework environments:**
```robot
&{DEV_CONFIG}    
...    base_url=https://dev-healthcare.example.com
...    api_url=https://dev-api-healthcare.example.com
...    db_host=dev-db.healthcare.com
```

### Browser Configuration

Support for multiple browsers:
- Chromium (default)
- Firefox
- WebKit/Safari

### Database Support

- PostgreSQL (primary)
- MySQL
- SQLite (for local testing)

## 📊 Reporting

### Built-in Reports
- **Robot Framework HTML Reports** - Detailed test execution reports
- **pytest HTML Reports** - API test results with screenshots
- **Allure Reports** - Advanced reporting with trends and history
- **Coverage Reports** - Code coverage for unit tests

### Report Locations
```
results/
├── robot-results/         # Robot Framework outputs
├── api-test-report.html   # API test results
├── allure-report/         # Allure HTML report
├── screenshots/           # Failure screenshots
└── logs/                 # Execution logs
```

## 🔒 Security & Compliance

### HIPAA Compliance Features
- **Audit Trail Logging** - All patient data access logged
- **Data Masking** - PII data masked in logs and screenshots
- **Secure Authentication** - Multi-factor authentication testing
- **Data Encryption** - Sensitive test data encryption
- **Access Control** - Role-based permission testing

### Security Testing
- Authentication and authorization
- SQL injection prevention
- XSS protection
- CSRF protection
- Security headers validation
- Session security

## 🏥 Healthcare-Specific Features

### Patient Data Management
- Complete patient lifecycle testing
- Medical history validation
- Medication management
- Allergy tracking
- Insurance verification

### Appointment System
- Provider scheduling
- Availability checking
- Conflict resolution
- Reminder systems
- Waitlist management

### Clinical Workflows
- Electronic Health Records (EHR)
- Clinical decision support
- Order management
- Results reporting

## 🛠️ Framework Features

### Custom Libraries
- **PlaywrightHealthcareLibrary** - Enhanced Playwright with healthcare-specific methods
- **DatabaseHealthcareLibrary** - Database operations with HIPAA audit support
- **APIHealthcareLibrary** - REST API testing with healthcare validations

### Data Management
- **DataFactory** - Realistic healthcare test data generation
- **TestDataManager** - Test data persistence and cleanup
- **SecurityHelper** - PII data encryption and masking

### Page Objects
- Maintainable UI test structure
- Reusable component interactions
- Healthcare-specific page elements

## 🔄 CI/CD Integration

### GitHub Actions Pipeline
- Automated test execution
- Multi-environment support
- Parallel test execution
- Security scanning
- Performance testing
- Report generation and publishing

### Pipeline Stages
1. **Lint & Security** - Code quality and security checks
2. **Unit Tests** - Fast feedback with coverage
3. **API Tests** - Backend validation
4. **UI Tests** - End-to-end workflows
5. **Database Tests** - Data integrity validation
6. **Performance Tests** - Load and stress testing
7. **Security Tests** - Penetration testing
8. **Report Generation** - Consolidated reporting

## 📈 Performance Testing

### Load Testing
- User simulation with realistic healthcare workflows
- Database performance under load
- API response time validation
- Resource utilization monitoring

### Tools Integration
- Locust for load testing
- pytest-benchmark for performance regression
- Database query optimization testing

## 🐛 Debugging & Troubleshooting

### Debug Features
- **Screenshot on Failure** - Automatic failure capture
- **Video Recording** - Complete test session recording
- **Detailed Logging** - Comprehensive execution logs
- **Test Data Preservation** - Failed test data retention

### Common Issues
1. **Environment Setup** - Check database connectivity and permissions
2. **Browser Issues** - Ensure Playwright browsers are installed
3. **Test Data** - Verify test database is initialized
4. **Permissions** - Confirm user roles and access rights

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Install pre-commit hooks: `pre-commit install`
4. Make changes and add tests
5. Run test suite: `python run_tests.py all`
6. Submit pull request

### Code Standards
- Follow PEP 8 for Python code
- Use Robot Framework style guide
- Maintain test coverage above 80%
- Include security and compliance considerations

### Testing Guidelines
- Write tests for new features
- Ensure HIPAA compliance
- Validate against multiple browsers
- Include negative test cases
- Test role-based access control

## 📚 Documentation

### Additional Resources
- [Robot Framework User Guide](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html)
- [Playwright Documentation](https://playwright.dev/python/)
- [pytest Documentation](https://docs.pytest.org/)
- [HIPAA Compliance Guidelines](https://www.hhs.gov/hipaa/)

### API Documentation
- Swagger/OpenAPI specifications
- FHIR resource documentation
- Authentication guides
- Rate limiting details

## 🆘 Support

### Getting Help
- Check the troubleshooting section
- Review existing issues in the repository
- Contact the QA team for healthcare-specific questions
- Review HIPAA compliance documentation

### Reporting Issues
1. Check existing issues first
2. Provide detailed reproduction steps
3. Include environment information
4. Attach relevant logs and screenshots
5. Specify healthcare compliance concerns

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Best Practices

### Healthcare Testing
- Always use de-identified test data
- Implement proper audit trails
- Validate data privacy controls
- Test all user roles and permissions
- Ensure compliance with healthcare regulations

### Test Automation
- Maintain test independence
- Use descriptive test names
- Implement proper cleanup
- Monitor test execution metrics
- Regular maintenance and updates

---

**Built with ❤️ for healthcare quality assurance teams**