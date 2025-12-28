#!/usr/bin/env python3
"""
test_agent.py - Test scenarios for the Agentic CX PoC

Run this after starting the server:
  python3 main.py  # In one terminal
  python3 test_agent.py  # In another terminal

Or use these cURL examples directly.
"""

import requests
import json
import time
from typing import Dict

BASE_URL = "http://localhost:8000"


def print_response(scenario: str, response: Dict):
    """Pretty-print test response."""
    print(f"\n{'='*70}")
    print(f"SCENARIO: {scenario}")
    print(f"{'='*70}")
    print(json.dumps(response, indent=2))
    print()


def test_scenario_1():
    """
    Scenario 1: Eligible customer with available slots
    Expected: Automatic resolution (AUTOMATE)
    """
    payload = {
        "customer_id": "123",
        "message": "I missed my appointment yesterday, can I rebook it?"
    }
    
    response = requests.post(f"{BASE_URL}/agentic-cx", json=payload).json()
    print_response("Eligible Customer - Automatic Resolution", response)
    
    # Assertions
    assert response["status"] == "resolved", "Should be resolved"
    assert response["decision_type"] == "automate", "Should automate"
    assert response["confidence"] > 0.9, "Should be high confidence"
    assert response["appointment_details"] is not None, "Should have appointment details"
    assert response["confirmation_sent"] is not None, "Should send confirmation"
    print("✅ Test passed: Automatic rebooking executed")


def test_scenario_2():
    """
    Scenario 2: Ineligible customer (too many missed appointments)
    Expected: Escalation (ESCALATE)
    """
    payload = {
        "customer_id": "456",
        "message": "I missed my appointment again, can you rebook me?"
    }
    
    response = requests.post(f"{BASE_URL}/agentic-cx", json=payload).json()
    print_response("Ineligible Customer - Escalation", response)
    
    # Assertions
    assert response["status"] == "escalated", "Should be escalated"
    assert response["decision_type"] == "escalate", "Should escalate"
    assert response["escalation_ticket"] is not None, "Should have escalation ticket"
    assert "too many misses" in response["decision"].lower() or "exceeded" in response["decision"].lower(), \
        "Should mention missed appointment limit"
    print("✅ Test passed: Escalated to human agent")


def test_scenario_3():
    """
    Scenario 3: Unknown/suspended customer
    Expected: Escalation (ESCALATE)
    """
    payload = {
        "customer_id": "789",
        "message": "Can you help me rebook my appointment?"
    }
    
    response = requests.post(f"{BASE_URL}/agentic-cx", json=payload).json()
    print_response("Suspended Account - Escalation", response)
    
    # Assertions
    assert response["status"] == "escalated", "Should be escalated"
    assert response["decision_type"] == "escalate", "Should escalate"
    assert response["escalation_ticket"] is not None, "Should have escalation ticket"
    print("✅ Test passed: Suspended account escalated")


def test_scenario_4():
    """
    Scenario 4: Non-existent customer
    Expected: Escalation (ESCALATE)
    """
    payload = {
        "customer_id": "999",
        "message": "I need to rebook my appointment"
    }
    
    response = requests.post(f"{BASE_URL}/agentic-cx", json=payload).json()
    print_response("Non-Existent Customer", response)
    
    # Assertions
    assert response["status"] == "escalated", "Should be escalated"
    assert response["decision_type"] == "escalate", "Should escalate"
    print("✅ Test passed: Unknown customer escalated")


def test_scenario_5():
    """
    Scenario 5: Intent detection - not a rebooking request
    Expected: Intent detection still works for other intents
    """
    payload = {
        "customer_id": "123",
        "message": "Can you tell me the address of your office?"
    }
    
    response = requests.post(f"{BASE_URL}/agentic-cx", json=payload).json()
    print_response("Unknown Intent", response)
    
    # Assertions
    assert response["intent"] == "unknown", "Should be unknown intent"
    print("✅ Test passed: Unknown intent handled gracefully")


def test_health_check():
    """Test the health check endpoint."""
    response = requests.get(f"{BASE_URL}/health").json()
    print_response("Health Check", response)
    
    assert response["status"] == "healthy", "Should be healthy"
    assert response["service"] == "Agentic CX PoC", "Correct service name"
    print("✅ Test passed: Health check successful")


def test_root_endpoint():
    """Test the root endpoint."""
    response = requests.get(f"{BASE_URL}/").json()
    print_response("Root Endpoint", response)
    
    assert "endpoints" in response, "Should have endpoints documentation"
    assert "example_request" in response, "Should have example request"
    print("✅ Test passed: Root endpoint works")


def run_all_tests():
    """Run all test scenarios."""
    print("\n" + "="*70)
    print("AGENTIC CX POC - TEST SUITE")
    print("="*70)
    print(f"\nConnecting to {BASE_URL}...")
    print("Make sure the server is running: python3 main.py\n")
    
    time.sleep(1)
    
    try:
        # Health check first
        test_health_check()
        test_root_endpoint()
        
        # Scenario tests
        test_scenario_1()
        test_scenario_2()
        test_scenario_3()
        test_scenario_4()
        test_scenario_5()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to the API server")
        print(f"   Make sure the server is running at {BASE_URL}")
        print("   Run: python3 main.py")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")


if __name__ == "__main__":
    run_all_tests()
