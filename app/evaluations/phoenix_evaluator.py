from phoenix.evals import ClassificationEvaluator
from phoenix.evals.metrics.faithfulness import FaithfulnessEvaluator
from phoenix.evals.llm import LLM
import pandas as pd

llm = LLM(provider="openai", model="gpt-4o-mini")

# ----------------------------
# 1️⃣ Faithfulness Check
# ----------------------------
def evaluate_claim_faithfulness(input_text: str, extracted_claim: str):
    evaluator = FaithfulnessEvaluator(llm=llm)
    result = evaluator.evaluate({
        "input": input_text,
        "output": extracted_claim,
    })
    return result[0].score


# ----------------------------
# 2️⃣ Decision Reasoning Quality
# ----------------------------
def evaluate_decision_reasoning(policy_text: str, decision_reason: str):
    evaluator = ClassificationEvaluator(
        name="decision_reasoning",
        llm=llm,
        prompt_template="""You are an expert insurance auditor.

Policy:
{policy_text}

Explanation:
{decision_reason}

Determine whether the explanation correctly follows the policy.
""",
        choices={"CORRECT_REASONING": 1, "INCORRECT_REASONING": 0},
    )
    result = evaluator.evaluate({
        "policy_text": policy_text,
        "decision_reason": decision_reason,
    })
    return result[0].label


# ----------------------------
# 3️⃣ Final Report Relevance (custom)
# ----------------------------
def evaluate_report_relevance(context: str, report_text: str):
    evaluator = ClassificationEvaluator(
        name="report_relevance",
        llm=llm,
        prompt_template="""Evaluate whether the report is relevant to the given context.

Context:
{context}

Report:
{report_text}

"relevant" means the report directly addresses the context.
"irrelevant" means the report does not address the context.
""",
        choices={"relevant": 1, "irrelevant": 0},
    )
    result = evaluator.evaluate({
        "context": context,
        "report_text": report_text,
    })
    return result[0].score