# Diagnostic Guide for LLM Response Parsing

This document explains how to interpret the diagnostic logs from the agentic-ai-cx system, especially when debugging LLM response issues.

## Overview

The system now includes comprehensive diagnostic logging to track:
1. LLM query initialization
2. LLM response reception
3. JSON parsing attempts
4. Validation failures
5. Error conditions

All diagnostics are logged to stdout (visible in Render logs) with a prefix of `🔍 DIAGNOSTIC:` for easy filtering.

## Diagnostic Events

### 1. LLM Query Events

#### `LLM_QUERY_START`
Logged when the LLM query begins. Shows which model is being used and message length.

```
🔍 DIAGNOSTIC: {
  "timestamp": "2024-01-15T10:30:45.123456",
  "event": "LLM_QUERY_START",
  "data": {
    "customer_id": "CUST123",
    "model": "models/gemini-1.5-flash",
    "message_length": 145
  }
}
```

**What to check:**
- Is the `model` correct? (Should be `models/gemini-1.5-flash` or similar)
- Is the `message_length` reasonable? (Very short might be truncated)

#### `LLM_RESPONSE_RECEIVED`
Logged immediately after receiving the LLM response. Shows response characteristics.

```
🔍 DIAGNOSTIC: {
  "timestamp": "2024-01-15T10:30:47.456789",
  "event": "LLM_RESPONSE_RECEIVED",
  "data": {
    "response_length": 287,
    "response_preview": "{\"intent\":\"complaint\",\"goal\":\"address customer concern\",...",
    "api_method": "generate_content"
  }
}
```

**What to check:**
- Is `response_length` > 0? (Empty response = LLM error)
- Does `response_preview` start with `{`? (Should be valid JSON start)
- Is `api_method` `generate_content` or `chat`? (Indicates which API was used)

#### `LLM_QUERY_ERROR`
Logged if the LLM query fails entirely.

```
🔍 DIAGNOSTIC: {
  "timestamp": "2024-01-15T10:30:46.000000",
  "event": "LLM_QUERY_ERROR",
  "data": {
    "error_type": "APIConnectionError",
    "error_message": "Failed to connect to API"
  }
}
```

**What to check:**
- `error_type`: Is it an API connection issue or a credential issue?
- `error_message`: Does it mention authentication or rate limiting?

### 2. Parsing Events

#### `PARSE_ATTEMPT_START`
Logged when parsing begins. Shows the first 150 characters of the response.

```
🔍 DIAGNOSTIC: {
  "timestamp": "2024-01-15T10:30:48.000000",
  "event": "PARSE_ATTEMPT_START",
  "data": {
    "response_length": 287,
    "response_preview": "{\"intent\":\"complaint\",\"goal\":\"address customer concern\",\"decision\":"
  }
}
```

**What to check:**
- Does `response_preview` show valid JSON format?
- Is there extra text before the `{`? (Indicates markdown wrapping or explanations)

#### `PARSE_SUCCESS`
Logged when JSON is successfully parsed and validated.

```
🔍 DIAGNOSTIC: {
  "timestamp": "2024-01-15T10:30:48.200000",
  "event": "PARSE_SUCCESS",
  "data": {
    "method": "direct_json"
  }
}
```

**Parsing Methods:**
- `direct_json`: Response was already valid JSON (best case)
- `markdown_extraction`: Had to extract from ````json...```` block
- `object_extraction`: Had to find `{` and `}` delimiters

#### `PARSE_FAILED_ALL_METHODS`
Logged when all parsing strategies fail.

```
🔍 DIAGNOSTIC: {
  "timestamp": "2024-01-15T10:30:48.300000",
  "event": "PARSE_FAILED_ALL_METHODS",
  "data": {
    "response_length": 500,
    "first_200_chars": "The customer wants to reschedule...",
    "last_100_chars": "...Please provide me with more details."
  }
}
```

**What to check:**
- Does `first_200_chars` show text explanation instead of JSON?
- Does `last_100_chars` show the LLM trying to explain its reasoning?
- Is the entire response plain text instead of JSON? (System prompt not working)

#### `PARSE_ERROR`
Logged when there's a parsing error.

```
🔍 DIAGNOSTIC: {
  "timestamp": "2024-01-15T10:30:48.000000",
  "event": "PARSE_ERROR",
  "data": {
    "reason": "empty_response"
  }
}
```

### 3. Validation Events

Validation errors are printed to stdout with `❌` prefixes:

```
❌ Missing required field: intent
❌ Invalid decision_type: AUTO
❌ Confidence out of range: 1.5
```

**What to check:**
- Which fields are missing? (Might indicate system prompt not being followed)
- Are enum values matching? (decision_type should be exactly AUTOMATE, ESCALATE, or CLARIFY)
- Is confidence a valid number between 0 and 1?

## Troubleshooting Guide

### Issue: "Failed to parse LLM response" Error

**Step 1: Check PARSE_FAILED_ALL_METHODS log**
- Look at the `first_200_chars` and `last_100_chars`
- If they show natural language instead of JSON, the LLM is ignoring the system prompt

**Step 2: Check PARSE_ATTEMPT_START preview**
- If it starts with text instead of `{`, the LLM wrapped the JSON in explanation
- This requires adjusting the system prompt to be more emphatic

**Step 3: Check if all three parsing methods failed**
- Direct JSON failed: Response isn't valid JSON
- Markdown extraction failed: No ````json...```` blocks found
- Object extraction failed: Can't find `{...}` delimiters

**Step 4: Consider the model access**
- Check if the API key has access to the model being used
- Run `python3 list_models.py` to verify available models

### Issue: Parsing succeeds but validation fails

**Check which field is missing:**
```
❌ Missing required field: decision_type
```

**Expected values for each field:**

| Field | Type | Valid Values | Example |
|-------|------|--------------|---------|
| intent | string | missed_appointment_rebook, complaint, general_inquiry, account_issue, unknown | "complaint" |
| goal | string | Any description | "address customer concern" |
| decision | string | Any description | "create support ticket" |
| decision_type | enum | AUTOMATE, ESCALATE, CLARIFY | "ESCALATE" |
| reasoning | string | Any explanation | "customer is upset" |
| recommended_action | string | rebook_appointment, escalate_to_human, request_clarification, other | "escalate_to_human" |
| confidence | number | 0.0 to 1.0 | 0.85 |

### Issue: Wrong model being used

**Check LLM_QUERY_START log:**
```
"model": "models/gemini-1.5-flash"
```

If you see a different model (like "gemini-pro" or "models/embedding-gecko-001"):
1. Your API key might not have access to the latest models
2. Run `python3 list_models.py` to see available models
3. Update the API key if needed (must be from aistudio.google.com)

## Log Analysis Tips

### Quick Render Log Filtering

In Render dashboard logs, filter by diagnostic events:
```
event: LLM_QUERY_START
event: PARSE_FAILED_ALL_METHODS
error
```

### Common Patterns

**Pattern 1: All requests parse successfully**
```
LLM_QUERY_START → LLM_RESPONSE_RECEIVED → PARSE_SUCCESS
✅ Parsing working correctly
```

**Pattern 2: Some requests fail parsing**
```
LLM_QUERY_START → LLM_RESPONSE_RECEIVED → PARSE_FAILED_ALL_METHODS
PARSE_ERROR details show explanation text instead of JSON
→ System prompt needs adjustment
```

**Pattern 3: LLM not called at all**
```
No LLM_QUERY_START events found
→ Request failed before reaching LLM (check middleware logs)
```

**Pattern 4: Missing fields**
```
PARSE_SUCCESS but ❌ Missing required field: decision_type
→ System prompt examples don't match validation rules
```

## System Prompt Effectiveness

The system prompt is designed to force JSON-only output. It includes:

1. **CRITICAL warnings** (repeated 3x in all caps)
2. **Concrete JSON examples** showing exact expected format
3. **Field requirements** with valid values for enums
4. **Explicit instructions** that response must start with `{` and end with `}`

If you see LLM returning explanations or wrapped JSON:
1. The system prompt isn't being followed
2. This might indicate a model/API mismatch (older Gemini version)
3. Try adding `temperature=0` to force more deterministic behavior
4. Consider testing with a different Gemini model version

## Next Steps

If you continue seeing parse failures after checking the logs:

1. **Share the PARSE_FAILED_ALL_METHODS log output** - This shows the exact format the LLM is returning
2. **Check LLM_QUERY_START/RESPONSE_RECEIVED** - Verify the model and response length
3. **Run list_models.py** - Confirm API key has proper model access
4. **Consider temperature=0** - Might help force deterministic JSON output

---

**Last Updated:** January 2024
**System Version:** With diagnostic logging (commit 2037779+)
