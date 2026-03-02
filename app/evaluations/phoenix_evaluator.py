from phoenix.evals import ClassificationEvaluator
from phoenix.evals.metrics.faithfulness import FaithfulnessEvaluator
from phoenix.evals.llm import LLM
from phoenix.client import Client
import pandas as pd

llm = LLM(provider="openai", model="gpt-4o-mini")
client = Client()


def log_annotation(span_id: str, name: str, label: str, score: float, explanation: str = ""):
    """Helper to log evaluation result as annotation to Phoenix."""
    annotations_df = pd.DataFrame([{
        "span_id": span_id,
        "name": name,
        "label": label,
        "score": score,
        "explanation": explanation,
    }])
    client.spans.log_span_annotations_dataframe(dataframe=annotations_df)


# ----------------------------
# 1️⃣ Faithfulness Check (added context)
# ----------------------------
def evaluate_claim_faithfulness(input_text: str, extracted_claim: str, reference_context: str, span_id: str = None):
    evaluator = FaithfulnessEvaluator(llm=llm)
    result = evaluator.evaluate({
        "input": input_text,
        "output": extracted_claim,
        "context": reference_context,
    })
    if span_id:
        log_annotation(span_id, "faithfulness", result[0].label, result[0].score, result[0].explanation)
    return result[0].score


# ----------------------------
# 2️⃣ Decision Reasoning Quality
# ----------------------------
def evaluate_decision_reasoning(policy_text: str, decision_reason: str, span_id: str = None):
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
    if span_id:
        log_annotation(span_id, "decision_reasoning", result[0].label, result[0].score, result[0].explanation)
    return result[0].label


# ----------------------------
# 3️⃣ Final Report Relevance
# ----------------------------
def evaluate_report_relevance(context: str, report_text: str, span_id: str = None):
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
    if span_id:
        log_annotation(span_id, "report_relevance", result[0].label, result[0].score, result[0].explanation)
    return result[0].score