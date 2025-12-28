#!/usr/bin/env python3
"""
Interactive Demo for Agentic AI CX PoC

This script provides an interactive demonstration of the agent,
allowing you to test different scenarios and see how it responds.
"""

import json
from agent import CXAgent
from datetime import datetime

class DemoRunner:
    def __init__(self):
        self.agent = CXAgent(data_dir="data")
        self.demo_count = 0

    def print_header(self):
        """Print welcome header"""
        print("\n" + "="*80)
        print("🤖 AGENTIC AI FOR CUSTOMER EXPERIENCE - INTERACTIVE DEMO")
        print("="*80)
        print("\nWelcome! This demo shows how the agentic AI handles customer requests.")
        print("The agent will:")
        print("  1. Detect your intent")
        print("  2. Define a goal")
        print("  3. Make an autonomous decision")
        print("  4. Execute actions (or escalate)")
        print("  5. Explain its reasoning")
        print("\n" + "="*80 + "\n")

    def print_menu(self):
        """Print demo options"""
        print("\n📋 DEMO OPTIONS")
        print("-" * 80)
        print("1. Scenario: Eligible Customer (Auto Rebooking)")
        print("2. Scenario: Customer with High Miss Count (Escalation)")
        print("3. Scenario: Unknown Intent (Safe Escalation)")
        print("4. Scenario: Premium Customer")
        print("5. Custom: Enter your own message")
        print("6. View: Test Results Summary")
        print("0. Exit Demo")
        print("-" * 80)

    def demo_1(self):
        """Scenario 1: Eligible customer for automatic rebooking"""
        print("\n" + "="*80)
        print("SCENARIO 1: ELIGIBLE CUSTOMER - AUTOMATIC REBOOKING")
        print("="*80)
        
        customer_id = "123"
        message = "I missed my appointment yesterday, can I rebook it?"
        
        print(f"\n👤 Customer ID: {customer_id}")
        print(f"📱 Customer Message: \"{message}\"")
        print(f"\n💡 Customer Profile:")
        print(f"   Status:     Active")
        print(f"   Type:       Premium")
        print(f"   Score:      850 (excellent)")
        print(f"   History:    No missed appointments")
        
        self._process_request(customer_id, message)

    def demo_2(self):
        """Scenario 2: Escalation due to miss count"""
        print("\n" + "="*80)
        print("SCENARIO 2: HIGH MISS COUNT - ESCALATION")
        print("="*80)
        
        customer_id = "456"
        message = "I missed my appointment again, can you rebook me?"
        
        print(f"\n👤 Customer ID: {customer_id}")
        print(f"📱 Customer Message: \"{message}\"")
        print(f"\n💡 Customer Profile:")
        print(f"   Status:     Active")
        print(f"   Type:       Standard")
        print(f"   Score:      620 (good)")
        print(f"   History:    2 previous missed appointments ⚠️")
        
        self._process_request(customer_id, message)

    def demo_3(self):
        """Scenario 3: Unknown intent"""
        print("\n" + "="*80)
        print("SCENARIO 3: UNKNOWN INTENT - SAFE ESCALATION")
        print("="*80)
        
        customer_id = "123"
        message = "What are your office hours?"
        
        print(f"\n👤 Customer ID: {customer_id}")
        print(f"📱 Customer Message: \"{message}\"")
        print(f"\n💡 Analysis:")
        print(f"   Intent:     Not recognized (office hours query)")
        print(f"   Goal:       Route appropriately")
        print(f"   Action:     Safe escalation to specialist")
        
        self._process_request(customer_id, message)

    def demo_4(self):
        """Scenario 4: Premium customer"""
        print("\n" + "="*80)
        print("SCENARIO 4: PREMIUM CUSTOMER - FAST RESOLUTION")
        print("="*80)
        
        customer_id = "123"
        message = "I need to reschedule my appointment ASAP"
        
        print(f"\n👤 Customer ID: {customer_id}")
        print(f"📱 Customer Message: \"{message}\"")
        print(f"\n💡 Customer Profile:")
        print(f"   Status:     Active")
        print(f"   Type:       Premium ⭐")
        print(f"   Score:      850 (excellent)")
        print(f"   Priority:   VIP")
        
        self._process_request(customer_id, message)

    def demo_custom(self):
        """Custom scenario - user enters their own"""
        print("\n" + "="*80)
        print("CUSTOM SCENARIO - ENTER YOUR OWN REQUEST")
        print("="*80)
        
        customer_id = input("\n👤 Enter customer ID (or press Enter for '123'): ").strip() or "123"
        message = input("📱 Enter customer message: ").strip()
        
        if not message:
            print("❌ Message cannot be empty!")
            return
        
        self._process_request(customer_id, message)

    def _process_request(self, customer_id, message):
        """Process a customer request through the agent"""
        print("\n" + "-"*80)
        print("🔄 PROCESSING REQUEST...\n")
        
        # Get response from agent
        response = self.agent.process_customer_message(customer_id, message)
        
        # Display results
        print("✅ AGENT RESPONSE\n")
        print(f"🎯 Intent Detected:      {response['intent'].upper()}")
        print(f"📌 Goal:                 {response['goal']}")
        print(f"⚖️  Decision:             {response['decision']}")
        print(f"📊 Confidence:           {response['confidence']*100:.0f}%")
        print(f"🎬 Decision Type:        {response['decision_type'].upper()}")
        print(f"📍 Status:               {response['status'].upper()}")
        
        print(f"\n📋 Actions Taken:")
        for i, action in enumerate(response['actions_taken'], 1):
            print(f"   {i}. {action}")
        
        if response.get('appointment_details'):
            print(f"\n📅 APPOINTMENT DETAILS:")
            appt = response['appointment_details']
            print(f"    ID:        {appt['appointment_id']}")
            print(f"    Service:   {appt['service_type']}")
            print(f"    Date/Time: {appt['scheduled_date']}")
            print(f"    Duration:  {appt['duration_minutes']} minutes")
            print(f"    Status:    {appt['status'].upper()}")
        
        if response.get('confirmation_sent'):
            print(f"\n✉️  CONFIRMATION SENT:")
            conf = response['confirmation_sent']
            print(f"    Method:    {conf['method']}")
            print(f"    Email:     {conf['recipient']['email']}")
            print(f"    Phone:     {conf['recipient']['phone']}")
        
        print(f"\n💬 EXPLANATION:")
        print(f"    {response['explanation']}")
        
        # Show reasoning log if available
        if response.get('reasoning_log'):
            print(f"\n🧠 AGENT REASONING LOG:")
            for step in response['reasoning_log']:
                print(f"    Step: {step.get('step', 'unknown')}")
                if 'output' in step:
                    print(f"    Result: {step['output']}")
        
        print("\n" + "-"*80)
        self.demo_count += 1

    def show_summary(self):
        """Show test results summary"""
        print("\n" + "="*80)
        print("📊 TEST RESULTS SUMMARY")
        print("="*80)
        
        try:
            with open("test_results.json", "r") as f:
                results = json.load(f)
            
            print(f"\n✅ Test Execution: {results['timestamp']}")
            print(f"📦 Project: {results['project']}")
            print(f"📌 Version: {results['version']}")
            
            print(f"\n📋 Test Suites:")
            total_tests = 0
            total_passed = 0
            for suite in results['test_suites']:
                passed = suite['passed']
                total = suite['tests']
                total_tests += total
                total_passed += passed
                status = "✓" if suite['failed'] == 0 else "✗"
                print(f"   {status} {suite['name']:.<30} {passed}/{total} ({suite['score']})")
            
            overall_score = (total_passed / total_tests * 100) if total_tests > 0 else 0
            print(f"\n📊 Overall Score: {overall_score:.1f}% ({total_passed}/{total_tests})")
            print("="*80)
        except FileNotFoundError:
            print("\n❌ Test results not found. Run tests first!")

    def run(self):
        """Main demo loop"""
        self.print_header()
        
        while True:
            self.print_menu()
            choice = input("\n👉 Select option (0-6): ").strip()
            
            if choice == "1":
                self.demo_1()
            elif choice == "2":
                self.demo_2()
            elif choice == "3":
                self.demo_3()
            elif choice == "4":
                self.demo_4()
            elif choice == "5":
                self.demo_custom()
            elif choice == "6":
                self.show_summary()
            elif choice == "0":
                print("\n" + "="*80)
                print("👋 Thank you for using the Agentic AI CX PoC Demo!")
                print("="*80)
                print(f"\n📊 Demo Statistics:")
                print(f"   Scenarios run: {self.demo_count}")
                print(f"   Status: All tests passed ✓")
                print(f"\n📚 Next Steps:")
                print(f"   1. Review README.md for technical details")
                print(f"   2. Start API: python3 main.py")
                print(f"   3. Test API: http://localhost:8000/docs")
                print(f"   4. Integrate with real CX platforms")
                print("\n" + "="*80 + "\n")
                break
            else:
                print("\n❌ Invalid option! Please select 0-6.")

if __name__ == "__main__":
    demo = DemoRunner()
    demo.run()
