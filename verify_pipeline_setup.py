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


def main():
    """Run pipeline verification checklist"""
    print("=" * 70)
    print("🏥 Healthcare Test Automation - Pipeline Setup Verification")
    print("=" * 70)
    print()
    
    checks_passed = 0
    total_checks = 0
    
    # Check 1: Pipeline file exists
    print("📋 STEP 1: Verifying Pipeline Files")
    print("-" * 70)
    total_checks += 1
    if check_file_exists(
        ".github/workflows/ci-cd-pipeline.yml",
        "Main CI/CD pipeline file"
    ):
        checks_passed += 1
    
    total_checks += 1
    if check_file_exists(
        ".github/workflows/README.md",
        "Pipeline documentation"
    ):
        checks_passed += 1
    
    total_checks += 1
    if check_file_exists(
        "GITHUB_PIPELINE_SETUP.md",
        "Setup guide"
    ):
        checks_passed += 1
    
    print()
    
    # Check 2: Pipeline configuration
    print("📋 STEP 2: Verifying Pipeline Configuration")
    print("-" * 70)
    
    pipeline_file = ".github/workflows/ci-cd-pipeline.yml"
    
    total_checks += 1
    if check_file_content(
        pipeline_file,
        "name: Healthcare Test Automation Pipeline",
        "Pipeline name configured"
    ):
        checks_passed += 1
    
    total_checks += 1
    if check_file_content(
        pipeline_file,
        "workflow_dispatch:",
        "Manual trigger enabled"
    ):
        checks_passed += 1
    
    total_checks += 1
    if check_file_content(
        pipeline_file,
        "test_suite:",
        "Test suite selection configured"
    ):
        checks_passed += 1
    
    total_checks += 1
    if check_file_content(
        pipeline_file,
        "lint-and-security:",
        "Code quality job configured"
    ):
        checks_passed += 1
    
    total_checks += 1
    if check_file_content(
        pipeline_file,
        "api-tests:",
        "API tests job configured"
    ):
        checks_passed += 1
    
    total_checks += 1
    if check_file_content(
        pipeline_file,
        "database-tests:",
        "Database tests job configured"
    ):
        checks_passed += 1
    
    total_checks += 1
    if check_file_content(
        pipeline_file,
        "postgres:15",
        "PostgreSQL service configured"
    ):
        checks_passed += 1
    
    print()
    
    # Check 3: Test files
    print("📋 STEP 3: Verifying Test Files")
    print("-" * 70)
    
    total_checks += 1
    if check_file_exists(
        "tests/api/test_simple_api.py",
        "API test file"
    ):
        checks_passed += 1
    
    total_checks += 1
    if check_file_exists(
        "verify_framework.py",
        "Framework verification script"
    ):
        checks_passed += 1
    
    print()
    
    # Check 4: Libraries
    print("📋 STEP 4: Verifying Custom Libraries")
    print("-" * 70)
    
    libraries = [
        ("libraries/APIHealthcareLibrary.py", "API Healthcare Library"),
        ("libraries/DatabaseHealthcareLibrary.py", "Database Healthcare Library"),
        ("libraries/PlaywrightHealthcareLibrary.py", "Playwright Healthcare Library"),
    ]
    
    for filepath, description in libraries:
        total_checks += 1
        if check_file_exists(filepath, description):
            checks_passed += 1
    
    print()
    
    # Check 5: Dependencies
    print("📋 STEP 5: Verifying Dependencies")
    print("-" * 70)
    
    total_checks += 1
    if check_file_exists(
        "requirements.txt",
        "Requirements file"
    ):
        checks_passed += 1
        
        # Check for key packages
        required_packages = [
            ("robotframework", "Robot Framework"),
            ("playwright", "Playwright"),
            ("pytest", "pytest"),
            ("requests", "requests"),
        ]
        
        for package, name in required_packages:
            total_checks += 1
            if check_file_content("requirements.txt", package, f"{name} in requirements"):
                checks_passed += 1
    
    print()
    
    # Final summary
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


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
