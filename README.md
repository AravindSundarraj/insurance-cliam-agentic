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
STEP 2 — Claim Extraction + Evaluation
🎯 Goal of Step 2

Convert raw claim text into:

Structured claim object

Validated claim

Evaluated quality

Fully traced in Phoenix

This step answers:

“Is this claim structured correctly and internally valid?”
Step 3 — Coverage classification
What Step 3 Is Trying to Achieve

Step 3 answers:

Based on the policy rules and the validated claim,
should the insurance company pay or reject this claim?
Step 4 — Payout calculation