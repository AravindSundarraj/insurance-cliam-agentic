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
STEP 4 — Fraud Detection & Risk Scoring Agent
🎯 Goal of Step 4

Step 4 takes:

✅ Policy (Step 1)

✅ Validated Claim (Step 2)

✅ Coverage Decision (Step 3)

and calculates:

Fraud risk score — Is this claim potentially suspicious?

Risk score — Does this claim pose financial or operational risk?

Recommendation — Flag for human review if necessary.

This improves decision quality, protects the insurer, and ensures compliance.
Why Step 4 Exists

Step 4 — Fraud Detection & Risk Scoring Agent as a complete Python module, following your agentic mindset and using Phoenix-style tracing via OpenTelemetry.

This step:

Evaluates fraud and risk scores deterministically

Uses optional LLM only to explain reasoning

Traces all steps in Phoenix (via OpenTelemetry)

Step 3 only checks:

Coverage types

Deductible

Coverage limit

But some claims may be legitimately covered but still high-risk or fraudulent:

Multiple small claims in a short period

Claims from blacklisted addresses or clients

Unusual claim patterns vs historical data

This gives you Step 4 fully functional:

Deterministic scoring

LLM explanation

Phoenix tracing

Clear recommendation for human review

step 5

Goal of Step 5

Take outputs from:

✅ Step 3 — Coverage Decision

✅ Step 4 — Fraud & Risk Scoring

And generate:

A structured, professional, audit-ready report
for customer OR internal insurance team.

Step 5:

✔ Summarizes results
✔ Explains decision clearly
✔ Formats for business use
✔ Creates transparency
✔ Ready for frontend or PDF

Your Full System Architecture Now
Step	Agent	Purpose
1	Policy Extraction	Understand policy
2	Claim Extraction + Validation	Structure & validate
3	Coverage Decision	Financial approval logic
4	Fraud & Risk Agent	Fraud & risk scoring
5	Reporting Agent	Generate final professional report