"""
GitHub Actions Workflow Validator
Validates the YAML syntax and structure of GitHub Actions workflows
"""

import sys
from pathlib import Path
import yaml


def get_trigger_count(triggers):
    """Get the count of triggers based on type"""
    if isinstance(triggers, str):
        return 1
    elif isinstance(triggers, list):
        return len(triggers)
    elif isinstance(triggers, dict):
        return len(triggers)
    else:
        return 0


def check_required_fields(workflow):
    """Check for required fields in workflow"""
    required = ['name', 'on', 'jobs']
    missing = [f for f in required if f not in workflow]
    if missing:
        for f in missing:
            print(f"ERROR: Missing required field: {f}")
        return False
    for f in required:
        print(f"OK: Found required field: {f}")
    return True


def validate_jobs(jobs):
    """Validate jobs structure"""
    print(f"\n Found {len(jobs)} jobs:")
    for job_name, job_config in jobs.items():
        print(f"  - {job_name}")
        if 'runs-on' not in job_config:
            print("    WARNING:  Warning: No 'runs-on' specified")
        if 'steps' not in job_config:
            print("    WARNING:  Warning: No 'steps' specified")


def print_triggers(triggers):
    """Print configured triggers"""
    print("\n Triggers configured:")
    if isinstance(triggers, dict):
        for trigger in triggers.keys():
            print(f"  - {trigger}")
    elif isinstance(triggers, list):
        for trigger in triggers:
            print(f"  - {trigger}")
    elif isinstance(triggers, str):
        print(f"  - {triggers}")


def print_env(env):
    """Print environment variables"""
    if env:
        print("\n Environment variables:")
        for key, value in env.items():
            print(f"  - {key}: {value}")
            print(f"    - Value: {value}")
            print(f"    - Type: {type(value).__name__}")
def validate_workflow(workflow_path):
    """Validate GitHub Actions workflow YAML file"""
    print(f"Validating: {workflow_path}")
    print("=" * 60)

    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            workflow = yaml.safe_load(f)

        if not check_required_fields(workflow):
            return False

        jobs = workflow.get('jobs', {})
        validate_jobs(jobs)

        triggers = workflow.get('on', {})
        print_triggers(triggers)

        env = workflow.get('env', {})
        print_env(env)

        print("\n" + "=" * 60)
        print("OK: Workflow validation PASSED")
        print(" Summary:")
        print(f"  - Jobs: {len(jobs)}")
        trigger_count = get_trigger_count(triggers)
        print(f"  - Triggers: {trigger_count}")
        print(f"  - Environment variables: {len(env)}")
        return True

    except yaml.YAMLError as e:
        print(f"ERROR: YAML syntax error: {e}")
        return False
    except FileNotFoundError:
        print(f"ERROR: File not found: {workflow_path}")
        return False
    except (OSError, IOError, KeyError, TypeError, ValueError) as e:
        print(f"ERROR: Validation error: {e}")
        return False


def main():
    """Main validation function"""
    print("Healthcare Test Automation - Workflow Validator")
    print("=" * 60)
    
    # Find workflow files
    workflows_dir = Path(__file__).parent
    workflow_files = list(workflows_dir.glob('*.yml')) + list(workflows_dir.glob('*.yaml'))
    
    if not workflow_files:
        print("ERROR: No workflow files found in .github/workflows/")
        return False
    
    print(f"\nFound {len(workflow_files)} workflow file(s):\n")
    
    all_valid = True
    for workflow_file in workflow_files:
        if not validate_workflow(workflow_file):
            all_valid = False
        print()
    
    if all_valid:
        print(" All workflows are valid!")
        return True

    print("WARNING:  Some workflows have issues")
    return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
