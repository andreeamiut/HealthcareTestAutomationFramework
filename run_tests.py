#!/usr/bin/env python3
"""
Test execution script for Healthcare Test Automation Framework
Provides convenient way to run different types of tests with various options
"""
import argparse
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Test directory constants
TESTS_API_DIR = "tests/api/"
TESTS_UI_DIR = "tests/ui/"
TESTS_INTEGRATION_DIR = "tests/integration/"


class HealthcareTestRunner:
    """Main test runner for healthcare test automation"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results_dir = self.project_root / "results"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup_environment(self):
        """Setup test environment and directories"""
        # Create results directories
        (self.results_dir / "screenshots").mkdir(parents=True, exist_ok=True)
        (self.results_dir / "logs").mkdir(parents=True, exist_ok=True)
        (self.results_dir / "videos").mkdir(parents=True, exist_ok=True)
        (self.results_dir / "allure-results").mkdir(parents=True, exist_ok=True)
        
        # Set environment variables
        os.environ['PYTHONPATH'] = str(self.project_root)
        
    def run_unit_tests(self, coverage=False, parallel=False):
        """Run unit tests with pytest"""
        print("🧪 Running unit tests...")
        
        cmd = ["python", "-m", "pytest", "tests/unit/", "-v"]
        
        if coverage:
            cmd.extend(["--cov=libraries", "--cov=utils", "--cov-report=html", "--cov-report=xml"])
        
        if parallel:
            cmd.extend(["-n", "auto"])
            
        cmd.extend([
            "--html=results/unit-test-report.html",
            "--self-contained-html",
            "--junit-xml=results/junit-unit.xml"
        ])
        
        return self._run_command(cmd)
    
    def run_api_tests(self, environment="dev", parallel=False):
        """Run API tests with pytest"""
        print("Running API tests...")
        
        cmd = ["python", "-m", "pytest", TESTS_API_DIR, "-v"]
        
        if parallel:
            cmd.extend(["-n", "auto"])
            
        cmd.extend([
            "--html=results/api-test-report.html",
            "--self-contained-html",
            "--junit-xml=results/junit-api.xml"
        ])
        
        # Set environment for API tests
        os.environ['ENVIRONMENT'] = environment
        
        return self._run_command(cmd)
    
    def run_ui_tests(self, environment="dev", browser="chromium", headless=True, 
                     parallel=False, tags=None):
        """Run UI tests with Robot Framework"""
        print("Running UI tests...")
        
        cmd = ["python", "-m", "robot"]
        
        # Output directory
        cmd.extend(["--outputdir", f"results/robot-{self.timestamp}"])
        
        # Report and log files
        cmd.extend(["--report", "report.html", "--log", "log.html"])
        
        # Variables
        cmd.extend([
            "--variable", f"ENVIRONMENT:{environment}",
            "--variable", f"BROWSER_TYPE:{browser}",
            "--variable", f"HEADLESS_MODE:{headless}"
        ])
        
        # Tags
        if tags:
            for tag in tags:
                cmd.extend(["--include", tag])
        
        # Parallel execution
        if parallel:
            cmd.extend(["--processes", "4"])
            
        cmd.append(TESTS_UI_DIR)
        
        return self._run_command(cmd)
    
    def run_database_tests(self, environment="dev"):
        """Run database tests with Robot Framework"""
        print("🗄️ Running database tests...")
        
        cmd = [
            "python", "-m", "robot",
            "--outputdir", f"results/db-{self.timestamp}",
            "--variable", f"ENVIRONMENT:{environment}",
            "--include", "database",
            "tests/database/"
        ]
        
        return self._run_command(cmd)
    
    def run_smoke_tests(self, environment="dev", browser="chromium"):
        """Run smoke tests across all test types"""
        print("💨 Running smoke tests...")
        
        success = True
        
        # API smoke tests
        cmd = [
            "python", "-m", "pytest", TESTS_API_DIR, "-v",
            "-m", "smoke",
            "--html=results/api-smoke-report.html",
            "--self-contained-html"
        ]
        if not self._run_command(cmd):
            success = False
            
        # UI smoke tests
        cmd = [
            "python", "-m", "robot",
            "--outputdir", f"results/smoke-{self.timestamp}",
            "--variable", f"ENVIRONMENT:{environment}",
            "--variable", f"BROWSER_TYPE:{browser}",
            "--include", "smoke",
            TESTS_UI_DIR
        ]
        if not self._run_command(cmd):
            success = False
            
        return success
    
    def run_all_tests(self, environment="dev", browser="chromium", coverage=False):
        """Run all test suites"""
        print("🚀 Running all tests...")
        
        results = {}
        
        # Unit tests
        results['unit'] = self.run_unit_tests(coverage=coverage)
        
        # API tests
        results['api'] = self.run_api_tests(environment=environment)
        
        # UI tests
        results['ui'] = self.run_ui_tests(environment=environment, browser=browser)
        
        # Database tests
        results['database'] = self.run_database_tests(environment=environment)
        
        # Generate summary
        self._generate_summary(results)
        
        return all(results.values())
    
    def run_regression_tests(self, environment="dev", browser="chromium"):
        """Run regression test suite"""
        print("🔄 Running regression tests...")
        
        success = True
        
        # API regression tests
        cmd = [
            "python", "-m", "pytest", TESTS_API_DIR, "-v",
            "-m", "regression",
            "--html=results/api-regression-report.html",
            "--self-contained-html"
        ]
        if not self._run_command(cmd):
            success = False
            
        # UI regression tests
        cmd = [
            "python", "-m", "robot",
            "--outputdir", f"results/regression-{self.timestamp}",
            "--variable", f"ENVIRONMENT:{environment}",
            "--variable", f"BROWSER_TYPE:{browser}",
            "--include", "regression",
            TESTS_UI_DIR
        ]
        if not self._run_command(cmd):
            success = False
            
        return success
    
    def generate_allure_report(self):
        """Generate Allure report if available"""
        print("📊 Generating Allure report...")
        
        if not self._command_exists("allure"):
            print("⚠️ Allure not found. Install Allure to generate reports.")
            return False
            
        cmd = ["allure", "generate", "results/allure-results", "--clean", "-o", "results/allure-report"]
        return self._run_command(cmd)
    
    def cleanup_test_data(self):
        """Clean up test data from database"""
        print("🧹 Cleaning up test data...")
        
        try:
            # Run cleanup SQL script
            cleanup_script = self.project_root / "data" / "sql_scripts" / "cleanup_test_data.sql"
            if cleanup_script.exists():
                cmd = [
                    "psql", 
                    "-h", os.getenv("DB_HOST", "localhost"),
                    "-U", os.getenv("DB_USER", "test_user"),
                    "-d", os.getenv("DB_NAME", "healthcare_test"),
                    "-f", str(cleanup_script)
                ]
                return self._run_command(cmd)
        except (FileNotFoundError, subprocess.SubprocessError) as e:
            print(f"⚠️ Cleanup failed: {e}")
            return False
            
        return True
    
    def _run_command(self, cmd):
        """Run a command and return success status"""
        try:
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, cwd=self.project_root)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed with exit code {e.returncode}")
            return False
        except OSError as e:
            print(f"❌ Error running command: {e}")
            return False
    
    def _command_exists(self, command):
        """Check if a command exists in PATH"""
        return subprocess.call(
            ["which", command], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        ) == 0
    
    def _generate_summary(self, results):
        """Generate test execution summary"""
        print("\n" + "="*50)
        print("TEST EXECUTION SUMMARY")
        print("="*50)
        
        for test_type, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{test_type.upper():15} {status}")
        
        overall = "✅ ALL PASSED" if all(results.values()) else "❌ SOME FAILED"
        print(f"\nOVERALL RESULT: {overall}")
        print("="*50)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Healthcare Test Automation Runner")
    
    parser.add_argument("test_type", choices=[
        "unit", "api", "ui", "database", "smoke", "regression", "all"
    ], help="Type of tests to run")
    
    parser.add_argument("--environment", "-e", default="dev",
                       choices=["dev", "staging", "prod"],
                       help="Target environment")
    
    parser.add_argument("--browser", "-b", default="chromium",
                       choices=["chromium", "firefox", "webkit"],
                       help="Browser for UI tests")
    
    parser.add_argument("--headless", action="store_true",
                       help="Run UI tests in headless mode")
    
    parser.add_argument("--parallel", "-p", action="store_true",
                       help="Run tests in parallel")
    
    parser.add_argument("--coverage", "-c", action="store_true",
                       help="Generate coverage report")
    
    parser.add_argument("--tags", "-t", nargs="+",
                       help="Robot Framework tags to include")
    
    parser.add_argument("--cleanup", action="store_true",
                       help="Clean up test data after execution")
    
    parser.add_argument("--allure", action="store_true",
                       help="Generate Allure report")
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = HealthcareTestRunner()
    runner.setup_environment()
    
    # Run tests based on type
    success = False
    
    if args.test_type == "unit":
        success = runner.run_unit_tests(coverage=args.coverage, parallel=args.parallel)
    elif args.test_type == "api":
        success = runner.run_api_tests(environment=args.environment, parallel=args.parallel)
    elif args.test_type == "ui":
        success = runner.run_ui_tests(
            environment=args.environment,
            browser=args.browser,
            headless=args.headless,
            parallel=args.parallel,
            tags=args.tags
        )
    elif args.test_type == "database":
        success = runner.run_database_tests(environment=args.environment)
    elif args.test_type == "smoke":
        success = runner.run_smoke_tests(environment=args.environment, browser=args.browser)
    elif args.test_type == "regression":
        success = runner.run_regression_tests(environment=args.environment, browser=args.browser)
    elif args.test_type == "all":
        success = runner.run_all_tests(
            environment=args.environment,
            browser=args.browser,
            coverage=args.coverage
        )
    
    # Generate Allure report if requested
    if args.allure:
        runner.generate_allure_report()
    
    # Cleanup if requested
    if args.cleanup:
        runner.cleanup_test_data()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()