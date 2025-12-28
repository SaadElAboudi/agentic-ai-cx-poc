#!/usr/bin/env python3
"""
Verification script to ensure agentic-ai-cx-poc is properly set up.
Checks all components and runs a sample agent request.
"""

import sys
import json
from pathlib import Path

def check_imports():
    """Verify all required modules can be imported."""
    print("Checking imports...")
    try:
        from agent import CXAgent
        print("  ✓ agent.CXAgent")
        from agent.reasoning import detect_intent, infer_goal
        print("  ✓ agent.reasoning")
        from agent.decision import make_decision
        print("  ✓ agent.decision")
        from agent.actions import get_customer_data, get_available_slots
        print("  ✓ agent.actions")
        import fastapi
        print("  ✓ fastapi")
        return True
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False

def check_files():
    """Verify all required files exist."""
    print("\nChecking files...")
    project_root = Path(__file__).parent
    required_files = [
        "main.py",
        "agent/agent.py",
        "agent/reasoning.py",
        "agent/decision.py",
        "agent/actions.py",
        "data/customers.json",
        "data/appointments.json",
        "prompts/agent_prompt.txt",
        "requirements.txt",
        "README.md",
        "QUICKSTART.md"
    ]
    
    all_exist = True
    for file in required_files:
        filepath = project_root / file
        if filepath.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (MISSING)")
            all_exist = False
    
    return all_exist

def check_data():
    """Verify mock data is valid JSON."""
    print("\nChecking mock data...")
    project_root = Path(__file__).parent
    data_files = ["data/customers.json", "data/appointments.json"]
    
    all_valid = True
    for file in data_files:
        filepath = project_root / file
        try:
            with open(filepath) as f:
                data = json.load(f)
            print(f"  ✓ {file} (valid JSON)")
        except Exception as e:
            print(f"  ✗ {file} (ERROR: {e})")
            all_valid = False
    
    return all_valid

def test_agent():
    """Run a sample agent request."""
    print("\nTesting agent logic...")
    try:
        import os
        from agent import CXAgent
        
        # Initialize agent with data directory
        project_root = Path(__file__).parent
        data_dir = project_root / "data"
        agent = CXAgent(data_dir=str(data_dir))
        
        # Test with a sample request
        response = agent.process_message(
            customer_id="123",
            message="I missed my appointment yesterday, can I rebook it?"
        )
        
        # Verify response structure
        required_fields = ["intent", "goal", "decision", "status", "actions_taken"]
        missing_fields = [f for f in required_fields if f not in response]
        
        if missing_fields:
            print(f"  ✗ Response missing fields: {missing_fields}")
            return False
        
        print(f"  ✓ Agent responded successfully")
        print(f"    Intent: {response['intent']}")
        print(f"    Goal: {response['goal']}")
        print(f"    Decision: {response['decision']}")
        print(f"    Status: {response['status']}")
        return True
    
    except Exception as e:
        print(f"  ✗ Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Agentic AI CX PoC - Setup Verification")
    print("=" * 60)
    
    results = {
        "imports": check_imports(),
        "files": check_files(),
        "data": check_data(),
        "agent": test_agent()
    }
    
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    for check, passed in results.items():
        status = "PASS ✓" if passed else "FAIL ✗"
        print(f"  {check:15} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All checks passed! Project is ready to use.")
        print("\nNext steps:")
        print("  1. python3 main.py")
        print("  2. http://localhost:8000/docs")
        print("  3. Test the /agentic-cx endpoint")
        return 0
    else:
        print("✗ Some checks failed. Please review the errors above.")
        print("\nTroubleshooting:")
        print("  - Ensure you're in the project root directory")
        print("  - Run: pip3 install -r requirements.txt")
        print("  - Check that all files were created correctly")
        return 1

if __name__ == "__main__":
    sys.exit(main())
