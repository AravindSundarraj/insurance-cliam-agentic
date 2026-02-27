from phoenix.evals import llm_classify
from phoenix.evals import HallucinationEvaluator
from phoenix.evals import RelevanceEvaluator

# clean implementation using LLM-as-Judge style evaluation:

# ----------------------------
# 1️⃣ Faithfulness Check (Step 2)
# ----------------------------

def evaluate_claim_faithfulness(input_text: str, extracted_claim: str):
    """
    Evaluates if structured claim is faithful to original claim text.
    """

    evaluator = HallucinationEvaluator()

    result = evaluator.evaluate(
        input=input_text,
        output=extracted_claim
    )

    return result.score


# ----------------------------
# 2️⃣ Decision Reasoning Quality (Step 3)
# ----------------------------

def evaluate_decision_reasoning(policy_text: str, decision_reason: str):
    """
    Uses LLM-as-Judge classification to evaluate reasoning quality.
    """

    labels = ["CORRECT_REASONING", "INCORRECT_REASONING"]

    result = llm_classify(
        input=policy_text,
        output=decision_reason,
        labels=labels
    )

    return result.label


# ----------------------------
# 3️⃣ Final Report Relevance (Step 5)
# ----------------------------

def evaluate_report_relevance(context: str, report_text: str):
    """
    Evaluates if final report is relevant to claim and decision.
    """

    evaluator = RelevanceEvaluator()

    result = evaluator.evaluate(
        input=context,
        output=report_text
    )

    return result.score