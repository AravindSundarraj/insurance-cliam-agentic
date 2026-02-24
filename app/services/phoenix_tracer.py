# Step 1.3 — Phoenix Tracer Setup
from phoenix.trace import trace

# What Phoenix Records Here

# Prompt

# LLM response

# Span name

# Latency

# Token usage (if configured)

# You will see this in Phoenix UI.

def traced_llm_call(prompt: str, llm_function):
    with trace("policy_extraction_llm_call") as span:
        span.set_input(prompt)
        output = llm_function(prompt)
        span.set_output(output)
        return output