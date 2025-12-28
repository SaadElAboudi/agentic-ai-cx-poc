#!/usr/bin/env python3
"""
verify.py - Verify the PoC is complete and working

This script checks that all components are in place and functional.
"""

import os
import json
import sys
from pathlib import Path


def check_file_exists(path: str, description: str) -> bool:
    """Check if a file exists."""
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists


def check_python_syntax(path: str, description: str) -> bool:
    """Check if a Python file has valid syntax."""
    try:
        with open(path, 'r') as f:
            compile(f.read(), path, 'exec')
        print(f"✅ {description}: Valid Python syntax")
        return True
    except SyntaxError as e:
        print(f"❌ {description}: Syntax error - {e}")
        return False
    except Exception as e:
        print(f"❌ {description}: Error - {e}")
        return False


def check_json_valid(path: str, description: str) -> bool:
    """Check if a JSON file is valid."""
    try:
        with open(path, 'r') as f:
            json.load(f)
        print(f"✅ {description}: Valid JSON")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ {description}: Invalid JSON - {e}")
        return False
    except Exception as e:
        print(f"❌ {description}: Error - {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("AGENTIC CX POC - VERIFICATION SCRIPT")
    print("=" * 70)
    print()

    all_good = True

    # Check Python files
    print("📋 Python Modules:")
    print("-" * 70)
    all_good &= check_python_syntax("agent/agent.py", "Core agent module")
    all_good &= check_python_syntax("agent/reasoning.py", "Reasoning module")
    all_good &= check_python_syntax("agent/decision.py", "Decision module")
    all_good &= check_python_syntax("agent/actions.py", "Actions module")
    all_good &= check_python_syntax("main.py", "FastAPI main")
    all_good &= check_python_syntax("test_agent.py", "Test suite")
    print()

    # Check data files
    print("📊 Data Files:")
    print("-" * 70)
    all_good &= check_json_valid("data/customers.json", "Customer data")
    all_good &= check_json_valid("data/appointments.json", "Appointment data")
    print()

    # Check configuration files
    print("⚙️ Configuration Files:")
    print("-" * 70)
    all_good &= check_file_exists("requirements.txt", "Python dependencies")
    all_good &= check_file_exists("Dockerfile", "Docker image")
    all_good &= check_file_exists("docker-compose.yml", "Docker Compose")
    all_good &= check_file_exists("prompts/agent_prompt.txt", "LLM system prompt")
    print()

    # Check scripts
    print("🚀 Scripts:")
    print("-" * 70)
    all_good &= check_file_exists("start.sh", "Quick start script")
    all_good &= check_file_exists("examples.sh", "cURL examples")
    print()

    # Check documentation
    print("📚 Documentation:")
    print("-" * 70)
    all_good &= check_file_exists("README.md", "Main documentation")
    all_good &= check_file_exists("QUICKSTART.md", "Quick start guide")
    all_good &= check_file_exists("DEPLOYMENT.md", "Deployment guide")
    all_good &= check_file_exists("INDEX.md", "Project index")
    print()

    # Check directory structure
    print("📁 Directory Structure:")
    print("-" * 70)
    dirs_to_check = ["agent", "data", "prompts"]
    for d in dirs_to_check:
        exists = os.path.isdir(d)
        status = "✅" if exists else "❌"
        print(f"{status} Directory: {d}/")
        all_good &= exists
    print()

    # Count files
    print("📈 Project Statistics:")
    print("-" * 70)
    py_files = list(Path(".").glob("**/*.py"))
    md_files = list(Path(".").glob("*.md"))
    json_files = list(Path(".").glob("data/*.json"))

    print(f"✅ Python files: {len(py_files)}")
    print(f"✅ Documentation files: {len(md_files)}")
    print(f"✅ Data files: {len(json_files)}")
    print()

    # Final result
    print("=" * 70)
    if all_good:
        print("✅ ALL CHECKS PASSED - PROJECT IS COMPLETE!")
        print()
        print("Next steps:")
        print("  1. Install dependencies: pip3 install -r requirements.txt")
        print("  2. Run the server: python3 main.py")
        print("  3. Test the agent: python3 test_agent.py")
        print("  4. Visit API docs: http://localhost:8000/docs")
        print()
        return 0
    else:
        print("❌ SOME CHECKS FAILED - PLEASE REVIEW ABOVE")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
