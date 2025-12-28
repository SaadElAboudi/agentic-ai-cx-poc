# Agentic AI CX PoC - Demo Guide

## 🎬 Running the Demo

There are **3 ways** to demonstrate this agentic AI system:

---

## Option 1: Interactive Demo (Recommended for Presentations)

The most engaging way to show the system working in real-time.

### Quick Start

```bash
cd /Users/saadelaboudi/Downloads/app\ howto/agentic_ai_cx_poc
python3 demo.py
```

### What You'll See

```
================================================================================
🤖 AGENTIC AI FOR CUSTOMER EXPERIENCE - INTERACTIVE DEMO
================================================================================

Welcome! This demo shows how the agentic AI handles customer requests.

📋 DEMO OPTIONS
────────────────────────────────────────────────────────────────────────────
1. Scenario: Eligible Customer (Auto Rebooking)
2. Scenario: Customer with High Miss Count (Escalation)
3. Scenario: Unknown Intent (Safe Escalation)
4. Scenario: Premium Customer
5. Custom: Enter your own message
6. View: Test Results Summary
0. Exit Demo

👉 Select option (0-6): _
```

### Demo Scenarios

#### 1️⃣ Eligible Customer - Automatic Rebooking
- **What it shows**: Agent autonomously rebooks an eligible customer
- **Timeline**: < 100ms
- **Result**: Appointment booked + confirmation sent

#### 2️⃣ High Miss Count - Escalation
- **What it shows**: Agent escalates a customer with miss history
- **Why**: Safety rule - customer exceeded miss limit
- **Result**: Escalated to human agent

#### 3️⃣ Unknown Intent - Safe Escalation
- **What it shows**: Agent safely escalates unknown requests
- **Why**: "What are your office hours?" is not rebooking
- **Result**: Safe escalation with low confidence

#### 4️⃣ Premium Customer - Fast Resolution
- **What it shows**: Agent handles premium customers quickly
- **Why**: VIP priority, active status
- **Result**: Fast automatic resolution

#### 5️⃣ Custom Scenario
- **What it shows**: Enter ANY message, see agent respond
- **Example**: "Can you help me change my appointment?"
- **Interactive**: You control the input

#### 6️⃣ View Results
- **What it shows**: Test results summary
- **Scores**: 100% pass rate (24/24 tests)
- **Details**: All 5 test suites

---

## Option 2: REST API Demo (For Developers)

Run the API server and test via HTTP requests.

### Step 1: Start the Server

```bash
python3 main.py
```

You should see:

```
=========================================================
Agentic CX PoC - Starting up
=========================================================
Data directory: /path/to/data
API available at: http://localhost:8000
Documentation: http://localhost:8000/docs
=========================================================
```

### Step 2: Open Interactive API Docs

Open your browser: **http://localhost:8000/docs**

You'll see the Swagger UI with the `/agentic-cx` endpoint ready to test.

### Step 3: Send Test Requests

#### Using Swagger UI (Visual)
1. Click on `/agentic-cx` endpoint
2. Click "Try it out"
3. Enter JSON:
```json
{
  "customer_id": "123",
  "message": "I missed my appointment yesterday, can I rebook it?"
}
```
4. Click "Execute"
5. See the response with full details

#### Using cURL (Command Line)

```bash
curl -X POST "http://localhost:8000/agentic-cx" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "123",
    "message": "I missed my appointment yesterday, can I rebook it?"
  }' | python3 -m json.tool
```

#### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/agentic-cx",
    json={
        "customer_id": "123",
        "message": "I missed my appointment yesterday, can I rebook it?"
    }
)

print(response.json())
```

### Example API Response

```json
{
  "intent": "missed_appointment_rebook",
  "goal": "Rebook the missed appointment with minimal customer effort",
  "decision": "Customer is eligible, slots are available, and data is complete. Proceeding with rebooking.",
  "decision_type": "automate",
  "actions_taken": [
    "check_eligibility",
    "find_available_slots",
    "rebook_appointment",
    "send_confirmation"
  ],
  "status": "resolved",
  "confidence": 0.95,
  "explanation": "I detected that you requested to rebook your missed appointment. You're eligible for rebooking, and I found available slots. I've automatically rebooked your appointment and sent a confirmation to your email and phone.",
  "appointment_details": {
    "appointment_id": "apt_20251228130828",
    "customer_id": "123",
    "service_type": "consultation",
    "scheduled_date": "2025-12-29T10:00:00Z",
    "status": "confirmed",
    "duration_minutes": 30
  },
  "confirmation_sent": {
    "success": true,
    "method": "email + SMS",
    "recipient": {
      "email": "alice@example.com",
      "phone": "+1-555-0001"
    }
  }
}
```

---

## Option 3: Python Test Suite

Run comprehensive tests programmatically.

### All Tests

```bash
python3 << 'EOF'
from agent import CXAgent

agent = CXAgent(data_dir="data")

# Test 1: Automatic Rebooking
response = agent.process_customer_message(
    customer_id="123",
    message="I missed my appointment yesterday, can I rebook it?"
)
print(f"Status: {response['status']}")  # Should be: resolved
print(f"Confidence: {response['confidence']}")  # Should be: 0.95

# Test 2: Escalation
response = agent.process_customer_message(
    customer_id="456",
    message="I missed my appointment again, can you rebook me?"
)
print(f"Status: {response['status']}")  # Should be: escalated

# Test 3: Unknown Intent
response = agent.process_customer_message(
    customer_id="123",
    message="What are your office hours?"
)
print(f"Status: {response['status']}")  # Should be: escalated
