# Quick Reference: LLM Parsing Troubleshooting

## ⚡ One-Minute Diagnostic Checklist

When you see "Failed to parse LLM response", check in order:

### 1. Check API Key Access (2 min)
```bash
python3 list_models.py
```
**Expected:** Shows `models/gemini-1.5-flash` or similar with `generateContent` support
**Problem:** Only shows `embedding-gecko-001`? → API key from wrong source
**Solution:** Get new key from https://aistudio.google.com (not makersuite.google.com)

### 2. Check Render Logs (2 min)
Go to Render dashboard → Logs, search for:
```
PARSE_FAILED_ALL_METHODS
```
**Look at:** `first_200_chars` field
- **If shows JSON:** System is working, parsing issue only
- **If shows text:** LLM ignoring system prompt (bigger issue)

### 3. Check Response Format (1 min)
```
LLM_RESPONSE_RECEIVED
  response_preview: "{\"intent\":\"..."
```
- **Starts with `{`?** Good, likely parsing issue
- **Starts with text?** LLM wrapped JSON in explanation

## 🔧 Common Issues & Fixes

| Issue | Symptom | Fix |
|-------|---------|-----|
| **Wrong API Key** | Only `embedding-gecko-001` in list_models | Get new key from aistudio.google.com |
| **LLM Adding Explanations** | PARSE_FAILED, response_preview shows text | Increase system prompt CRITICAL warnings or use temperature=0 |
| **Missing Fields** | Validation error "Missing field: X" | Check system prompt examples match required fields |
| **Wrong Model** | LLM_QUERY_START shows `gemini-pro` | May indicate old API or wrong key access level |
| **Empty Response** | PARSE_ERROR reason: "empty_response" | LLM crashed, check for API errors before this |
| **Invalid JSON** | Direct parse failed, can't extract | Check for escaped quotes or special characters in response |

## 📊 Expected Log Pattern

**✅ Healthy System:**
```
LLM_QUERY_START {"model": "models/gemini-1.5-flash"}
LLM_RESPONSE_RECEIVED {"response_preview": "{\"intent\": ..."}
PARSE_ATTEMPT_START {"response_length": 287}
PARSE_SUCCESS {"method": "direct_json"}
✅ Response validation passed
```

**⚠️ Parsing Issues:**
```
LLM_QUERY_START {"model": "models/gemini-1.5-flash"}
LLM_RESPONSE_RECEIVED {"response_preview": "The customer wants..."}  ← Problem: text instead of JSON
PARSE_ATTEMPT_START {"response_length": 500}
PARSE_FAILED_ALL_METHODS {"first_200_chars": "The customer..."}
```

**❌ API Key Issues:**
```
LLM_QUERY_ERROR {"error_type": "APIError", "error_message": "..."}
```

## 🔍 Diagnostic Log Locations

### Production (Render)
```
Render Dashboard
  → Project: agentic-ai-cx-poc
  → Logs tab
  → Search: "DIAGNOSTIC" or "PARSE_"
```

### Local (Development)
```bash
# After running application:
tail -f llm_diagnostics.log | grep PARSE

# Or parse all events:
cat llm_diagnostics.log | jq '.event'
```

## 📋 Field Validation Reference

```
Required Fields (ALL must be present):
├─ intent: missed_appointment_rebook | complaint | general_inquiry | account_issue | unknown
├─ goal: any string (e.g., "address concern")
├─ decision: any string (e.g., "escalate to agent")
├─ decision_type: AUTOMATE | ESCALATE | CLARIFY (UPPERCASE)
├─ reasoning: any string (e.g., "customer upset")
├─ recommended_action: rebook_appointment | escalate_to_human | request_clarification | other
└─ confidence: number 0.0 to 1.0 (not string)
```

## 🎯 Quick Fixes (In Order of Likelihood)

### 1. System Prompt Not Working
**Check:** Does `first_200_chars` in PARSE_FAILED show plain text?
```python
# In llm_agent.py, increase urgency:
self.system_prompt = """⚠️⚠️⚠️ CRITICAL: ONLY RESPOND WITH JSON ⚠️⚠️⚠️
...
generation_config=GenerationConfig(temperature=0)  # More deterministic
```

### 2. API Key Wrong Source
**Check:** Does `list_models.py` show only embedding models?
```bash
# Solution:
export GOOGLE_API_KEY="YOUR_NEW_KEY_FROM_aistudio.google.com"
python3 list_models.py
```

### 3. Parsing Logic Edge Case
**Check:** Which parse method failed? (direct_json | markdown | object)
```python
# If markdown extraction needed:
# → LLM returning code blocks: maybe models have changed
# → Try extracting better

# If object extraction needed:
# → LLM returning explanation before/after JSON: prompt needs work
```

### 4. Model Compatibility
**Check:** LLM_QUERY_START shows different model than expected?
```python
# In llm_agent.py:
return "models/gemini-1.5-flash"  # Hardcode if auto-detect failing
```

## 📞 When to Ask for Help

**Gather this info first:**

1. Full PARSE_FAILED_ALL_METHODS event:
```json
{
  "response_length": xxx,
  "first_200_chars": "...",
  "last_100_chars": "..."
}
```

2. Output of `list_models.py`

3. Output of `LLM_RESPONSE_RECEIVED` for same request

4. Was this working before? When did it break?

## 💡 Pro Tips

- **Monitor for patterns:** If 50% of requests fail parsing, system prompt issue
- **Check confidence values:** Consistently 0.0 suggests error fallback path
- **Watch for API rate limits:** May see timeouts in LLM_QUERY_ERROR
- **Local testing first:** Test with `generate_content()` API directly before deploying
- **Temperature matters:** 0.7 allows creativity, 0.0 more deterministic JSON

---

**Quick Links:**
- Full guide: See `DIAGNOSTIC_GUIDE.md`
- Session notes: See `SESSION_SUMMARY.md`
- System examples: See `COMPREHENSIVE_DOCUMENTATION.md`
- Model listing: Run `python3 list_models.py`
