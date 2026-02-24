# insurance-cliam-agentic
insurance-cliam-agentic
Step 1:

User uploads raw policy
        ↓
Document loader extracts text
        ↓
Policy Extraction Agent calls LLM
        ↓
LLM returns structured JSON
        ↓
Validate JSON using schema
        ↓
Return Policy object

🔍 What Phoenix Trace Looks Like

In Phoenix UI, you will see:

claim_review_workflow
 └── policy_extraction_llm_call
        - input: full prompt
        - output: JSON result
        - latency
        - token count

After Step 1:

What We Have Achieved After Step 1

Given any raw policy text, we now get:

Policy(
    coverage_types=["accidental damage"],
    exclusions=["intentional damage"],
    deductible=500,
    coverage_limit=10000,
    policy_number="ABC123"
)

This becomes the foundation for:

Step 2 — Claim understanding
Step 3 — Coverage classification
Step 4 — Payout calculation