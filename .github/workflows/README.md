# 🏥 Healthcare Test Automation CI/CD Pipeline

## 📋 Overview

This GitHub Actions workflow provides comprehensive continuous integration and testing for the Healthcare Test Automation Framework. It runs automatically on code changes and can be triggered manually with custom test suite selection.

## 🚀 Pipeline Features

### Automated Triggers
- **Push Events**: Runs on `main`, `develop`, and `feature/*` branches
- **Pull Requests**: Validates PRs to `main` and `develop`
- **Scheduled**: Daily execution at 2 AM UTC
- **Manual**: On-demand execution via workflow_dispatch

### Test Suites Available
- **all**: Complete test suite (default)
- **smoke**: Quick smoke tests for rapid feedback
- **api**: API-focused tests
- **integration**: End-to-end integration tests
- **security**: Security and HIPAA compliance tests

## 📊 Pipeline Jobs

### 1. Setup & Validation
- Generates dependency cache keys
- Validates Python environment
- Displays workflow information

### 2. Code Quality & Security
- **Black**: Code formatting check
- **isort**: Import organization validation
- **Flake8**: PEP 8 style guide enforcement
- **Pylint**: Advanced static code analysis
- **Bandit**: Security vulnerability scanning
- **Safety**: Dependency security checks

### 3. Framework Verification
- Validates all custom libraries import correctly
- Tests framework component instantiation
- Verifies core dependencies

### 4. API Tests
- Executes pytest-based API test suite
- Generates HTML and JSON test reports
- Publishes test results to PR comments
- Supports smoke, api, and security markers

### 5. Database Tests
- Spins up PostgreSQL 15 test database
- Validates database connectivity
- Tests DatabaseHealthcareLibrary functionality
- Environment variables for DB configuration

### 6. Integration Tests
- Runs full end-to-end test scenarios
- Executes only on push/manual triggers
- Tests cross-component integrations

### 7. Test Summary
- Aggregates all test results
- Generates GitHub step summary
- Lists available artifacts
- Displays build information

### 8. Notifications
- Sends notifications on completion
- Displays results for all test jobs
- Runs on scheduled and push events

## 🎯 Usage

### Running Manually

1. Go to **Actions** tab in GitHub
2. Select "Healthcare Test Automation Pipeline"
3. Click "Run workflow"
4. Select test suite:
   - `all`: Full test execution
   - `smoke`: Quick validation
   - `api`: API tests only
   - `integration`: Integration tests
   - `security`: Security tests
5. Click "Run workflow"

### Viewing Results

#### Test Reports
After pipeline completion, download artifacts:
- **security-reports**: Bandit and Safety scan results
- **api-test-reports**: HTML and JSON test reports
- **integration-test-reports**: Integration test HTML reports

#### GitHub Summary
Each workflow run generates a step summary with:
- Test execution results table
- Artifact list
- Build information (commit, branch, author)

#### PR Comments
For pull requests, test results are automatically posted as comments showing:
- Pass/fail status
- Test counts
- Failed test details

## 🔧 Configuration

### Environment Variables
```yaml
PYTHON_VERSION: '3.11'
ENVIRONMENT: 'ci'
```

### Database Service
PostgreSQL 15 container with:
- **Host**: localhost
- **Port**: 5432
- **Database**: healthcare_test
- **User**: test_user
- **Password**: test_password

### Artifact Retention
- Security reports: 30 days
- Test reports: 30 days

## 📈 Best Practices

### Before Pushing Code
1. Run tests locally: `python -m pytest tests/`
2. Check code formatting: `black --check .`
3. Validate imports: `isort --check-only .`
4. Run security scan: `bandit -r libraries/ utils/`

### Pull Request Guidelines
1. Ensure all checks pass before requesting review
2. Review security scan reports for vulnerabilities
3. Check code coverage in test reports
4. Address any linting warnings

### Scheduled Runs
- Daily runs help catch:
  - Dependency updates breaking tests
  - Environment drift issues
  - Flaky test detection

## 🛠️ Troubleshooting

### Common Issues

#### Pipeline Fails on Import
- **Cause**: Missing dependency in requirements.txt
- **Solution**: Add package to requirements.txt and commit

#### Database Connection Fails
- **Cause**: PostgreSQL service not ready
- **Solution**: Check health checks in workflow YAML

#### Test Timeout
- **Cause**: Long-running test or infinite loop
- **Solution**: Add timeout to pytest command

#### Linting Errors
- **Cause**: Code doesn't meet style guidelines
- **Solution**: Run `black .` and `isort .` locally

### Debug Mode

To enable debug logging:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add variable: `ACTIONS_STEP_DEBUG` = `true`

## 📞 Support

For pipeline issues:
1. Check workflow logs in Actions tab
2. Review error messages in failed jobs
3. Download and examine test report artifacts
4. Check database connectivity in logs

## 🔒 Security

- All secrets stored in GitHub Secrets
- Security scans run on every commit
- Dependency vulnerability checks
- HIPAA compliance validation in tests

## 📝 Maintenance

### Updating Dependencies
```bash
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
```

### Modifying Pipeline
1. Edit `.github/workflows/ci-cd-pipeline.yml`
2. Test locally using [act](https://github.com/nektos/act)
3. Commit and push changes
4. Monitor first run for issues

## 🎯 Success Criteria

Pipeline succeeds when:
- ✅ All code quality checks pass
- ✅ No security vulnerabilities found
- ✅ Framework verification completes
- ✅ All API tests pass
- ✅ Database connectivity confirmed
- ✅ Integration tests complete (on push)

---

**Last Updated**: 2024-01-20
**Pipeline Version**: 1.0.0
**Maintained By**: Healthcare Test Automation Team
