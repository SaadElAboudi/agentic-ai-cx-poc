#!/bin/bash

# CURL Examples for Agentic CX PoC
# Use these to test the agent from the command line

BASE_URL="http://localhost:8000"

echo "Agentic CX PoC - cURL Examples"
echo "================================"
echo ""
echo "Make sure the server is running:"
echo "  python3 main.py"
echo ""

# Example 1: Health Check
echo "1. Health Check"
echo "   Command:"
echo "   curl $BASE_URL/health"
echo ""
curl -s "$BASE_URL/health" | jq .
echo ""
echo ""

# Example 2: Root Endpoint
echo "2. Root Endpoint (API Info)"
echo "   curl $BASE_URL/"
echo ""
curl -s "$BASE_URL/" | jq .
echo ""
echo ""

# Example 3: Eligible Customer (Auto Resolution)
echo "3. Eligible Customer - Automatic Rebooking"
echo "   Request:"
cat <<'EOF'
curl -X POST "$BASE_URL/agentic-cx" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "123",
    "message": "I missed my appointment yesterday, can I rebook it?"
  }'
EOF
echo ""
echo "   Response:"
curl -s -X POST "$BASE_URL/agentic-cx" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "123",
    "message": "I missed my appointment yesterday, can I rebook it?"
  }' | jq .
echo ""
echo ""

# Example 4: Ineligible Customer (Escalation)
echo "4. Ineligible Customer (Too Many Misses) - Escalation"
echo "   Request:"
cat <<'EOF'
curl -X POST "$BASE_URL/agentic-cx" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "456",
    "message": "I missed my appointment again, can you rebook me?"
  }'
EOF
echo ""
echo "   Response:"
curl -s -X POST "$BASE_URL/agentic-cx" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "456",
    "message": "I missed my appointment again, can you rebook me?"
  }' | jq .
echo ""
echo ""

# Example 5: Unknown Customer (Escalation)
echo "5. Unknown Customer - Escalation"
echo "   Request:"
cat <<'EOF'
curl -X POST "$BASE_URL/agentic-cx" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "999",
    "message": "I need to rebook my appointment"
  }'
EOF
echo ""
echo "   Response:"
curl -s -X POST "$BASE_URL/agentic-cx" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "999",
    "message": "I need to rebook my appointment"
  }' | jq .
echo ""
echo ""

# Example 6: Suspended Account (Escalation)
echo "6. Suspended Account - Escalation"
echo "   Request:"
cat <<'EOF'
curl -X POST "$BASE_URL/agentic-cx" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "789",
    "message": "Can you help me rebook?"
  }'
EOF
echo ""
echo "   Response:"
curl -s -X POST "$BASE_URL/agentic-cx" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "789",
    "message": "Can you help me rebook?"
  }' | jq .
echo ""
echo ""

# Example 7: Unknown Intent
echo "7. Unknown Intent"
echo "   Request:"
cat <<'EOF'
curl -X POST "$BASE_URL/agentic-cx" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "123",
    "message": "What are your office hours?"
  }'
EOF
echo ""
echo "   Response:"
curl -s -X POST "$BASE_URL/agentic-cx" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "123",
    "message": "What are your office hours?"
  }' | jq .
echo ""
echo ""

echo "================================"
echo "All examples completed!"
echo "For interactive testing, visit: http://localhost:8000/docs"
