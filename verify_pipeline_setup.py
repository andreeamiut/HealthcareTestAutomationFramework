#!/usr/bin/env python3
"""
GitHub Actions Pipeline Verification Checklist
Ensures the CI/CD pipeline is properly configured
"""

from pathlib import Path


def check_file_exists(filepath, description):
    """Check if a file exists and report status"""
    exists = Path(filepath).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists


def check_file_content(filepath, search_text, description):
    """Check if file contains specific text"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            found = search_text in content
            status = "✅" if found else "❌"
            print(f"{status} {description}")
            return found
    except FileNotFoundError:
        print(f"❌ {description} - File not found")
        return False


def verify_pipeline_files():
    """Verify pipeline files exist"""
    print("📋 STEP 1: Verifying Pipeline Files")
    print("-" * 70)
    
    files = [
        (".github/workflows/ci-cd-pipeline.yml", "Main CI/CD pipeline file"),
        (".github/workflows/README.md", "Pipeline documentation"),
        ("GITHUB_PIPELINE_SETUP.md", "Setup guide"),
    ]
    
    passed = sum(1 for filepath, desc in files if check_file_exists(filepath, desc))
    print()
    return passed, len(files)


def verify_pipeline_configuration():
    """Verify pipeline configuration"""
    print("📋 STEP 2: Verifying Pipeline Configuration")
    print("-" * 70)
    
    pipeline_file = ".github/workflows/ci-cd-pipeline.yml"
    checks = [
        ("name: Healthcare Test Automation Pipeline", "Pipeline name configured"),
        ("workflow_dispatch:", "Manual trigger enabled"),
        ("test_suite:", "Test suite selection configured"),
        ("lint-and-security:", "Code quality job configured"),
        ("api-tests:", "API tests job configured"),
        ("database-tests:", "Database tests job configured"),
        ("postgres:15", "PostgreSQL service configured"),
    ]
    
    passed = sum(1 for text, desc in checks if check_file_content(pipeline_file, text, desc))
    print()
    return passed, len(checks)


def verify_test_files():
    """Verify test files exist"""
    print("📋 STEP 3: Verifying Test Files")
    print("-" * 70)
    
    files = [
        ("tests/api/test_simple_api.py", "API test file"),
        ("verify_framework.py", "Framework verification script"),
    ]
    
    passed = sum(1 for filepath, desc in files if check_file_exists(filepath, desc))
    print()
    return passed, len(files)


def verify_libraries():
    """Verify custom libraries exist"""
    print("📋 STEP 4: Verifying Custom Libraries")
    print("-" * 70)
    
    libraries = [
        ("libraries/APIHealthcareLibrary.py", "API Healthcare Library"),
        ("libraries/DatabaseHealthcareLibrary.py", "Database Healthcare Library"),
        ("libraries/PlaywrightHealthcareLibrary.py", "Playwright Healthcare Library"),
    ]
    
    passed = sum(1 for filepath, desc in libraries if check_file_exists(filepath, desc))
    print()
    return passed, len(libraries)


def verify_dependencies():
    """Verify dependencies"""
    print("📋 STEP 5: Verifying Dependencies")
    print("-" * 70)
    
    passed = 0
    total = 1
    
    if check_file_exists("requirements.txt", "Requirements file"):
        passed += 1
        
        required_packages = [
            ("robotframework", "Robot Framework"),
            ("playwright", "Playwright"),
            ("pytest", "pytest"),
            ("requests", "requests"),
        ]
        
        total += len(required_packages)
        passed += sum(1 for pkg, name in required_packages 
                     if check_file_content("requirements.txt", pkg, f"{name} in requirements"))
    
    print()
    return passed, total


def print_summary(checks_passed, total_checks):
    """Print verification summary"""
    print("=" * 70)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 70)
    print(f"Total Checks: {total_checks}")
    print(f"Passed: {checks_passed}")
    print(f"Failed: {total_checks - checks_passed}")
    print(f"Success Rate: {(checks_passed/total_checks)*100:.1f}%")
    print()
    
    if checks_passed == total_checks:
        print("🎉 ALL CHECKS PASSED! Pipeline is ready to use!")
        print()
        print("Next Steps:")
        print("1. Commit and push to GitHub")
        print("2. Go to Actions tab")
        print("3. Watch the pipeline run automatically")
        print("4. Or trigger manually via 'Run workflow' button")
        return True
    else:
        print("⚠️  Some checks failed. Please review the issues above.")
        print()
        print("Troubleshooting:")
        print("- Ensure all files are created")
        print("- Check file paths are correct")
        print("- Verify YAML syntax in pipeline file")
        return False


def main():
    """Run pipeline verification checklist"""
    print("=" * 70)
    print("🏥 Healthcare Test Automation - Pipeline Setup Verification")
    print("=" * 70)
    print()
    
    checks_passed = 0
    total_checks = 0
    
    # Run all verification steps
    passed, total = verify_pipeline_files()
    checks_passed += passed
    total_checks += total
    
    passed, total = verify_pipeline_configuration()
    checks_passed += passed
    total_checks += total
    
    passed, total = verify_test_files()
    checks_passed += passed
    total_checks += total
    
    passed, total = verify_libraries()
    checks_passed += passed
    total_checks += total
    
    passed, total = verify_dependencies()
    checks_passed += passed
    total_checks += total
    
    return print_summary(checks_passed, total_checks)


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
