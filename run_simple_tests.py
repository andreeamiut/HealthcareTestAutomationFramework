"""
Simple Test Runner for Healthcare Framework
Runs verification tests and generates a basic report
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success/failure"""
    print(f"\n{'='*70}")
    print(f"🧪 {description}")
    print(f"{'='*70}")
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}\n")
    
    try:
        # Convert string command to list for safer execution
        if isinstance(cmd, str):
            cmd = cmd.split()
        
        result = subprocess.run(
            cmd,
            shell=False,  # ✅ SECURITY FIX: Removed shell=True
            capture_output=True,
            text=True,
            check=False
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED (Exit code: {result.returncode})")
            return False
    except (OSError, subprocess.SubprocessError) as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("HEALTHCARE TEST AUTOMATION FRAMEWORK - TEST EXECUTION")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Ensure results directory exists
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    results = {}
    
    # 1. Framework Verification
    results['Framework Verification'] = run_command(
        ["python", "verify_framework.py"],
        "Framework Verification Tests"
    )
    
    # 2. Python Unit Tests (if they exist)
    unit_test_dir = Path("tests/unit")
    if unit_test_dir.exists():
        results['Unit Tests'] = run_command(
            ["python", "-m", "pytest", "tests/unit/", "-v", 
             "--html=results/unit-test-report.html", "--self-contained-html"],
            "Python Unit Tests"
        )
    else:
        print("\n⚠️  No unit tests directory found - skipping")
        results['Unit Tests'] = None
    
    # 3. API Tests
    results['API Tests'] = run_command(
        ["python", "-m", "pytest", "tests/api/", "-v", 
         "--html=results/api-test-report.html", "--self-contained-html"],
        "Healthcare API Tests"
    )
    
    # 4. Library Import Tests
    results['Library Tests'] = run_command(
        ["python", "-c", 
         "from libraries.APIHealthcareLibrary import APIHealthcareLibrary; "
         "from libraries.DatabaseHealthcareLibrary import DatabaseHealthcareLibrary; "
         "from libraries.PlaywrightHealthcareLibrary import PlaywrightHealthcareLibrary; "
         "print('All libraries imported successfully!')"],
        "Custom Library Import Tests"
    )
    
    # Print Summary
    print("\n" + "="*70)
    print("TEST EXECUTION SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    total = len([v for v in results.values() if v is not None])
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASSED"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⏭️  SKIPPED"
        print(f"{test_name:<40} {status}")
    
    print("="*70)
    print(f"Total: {passed}/{total} passed, {failed} failed, {skipped} skipped")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Print report locations
    if any(results.values()):
        print("\n📊 Test Reports Generated:")
        print("  - Verification: Console output above")
        if (results_dir / "unit-test-report.html").exists():
            print(f"  - Unit Tests: {results_dir / 'unit-test-report.html'}")
        if (results_dir / "api-test-report.html").exists():
            print(f"  - API Tests: {results_dir / 'api-test-report.html'}")
    
    # Exit with appropriate code
    if failed > 0:
        print("\n⚠️  Some tests failed. Review the output above for details.")
        return 1
    elif passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n✅ All executed tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
