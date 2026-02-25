# Step 1.3 — Phoenix Tracer Setup
#from phoenix.trace import trace
from opentelemetry import trace
from openinference.semconv.trace import SpanAttributes
from phoenix.otel import register

# What Phoenix Records Here

# Prompt

# LLM response

# Span name

# Latency

# Token usage (if configured)

# You will see this in Phoenix UI.


tracer_provider = register(project_name="insurance-cliam-agentic", auto_instrument=True)

tracer = trace.get_tracer("insurance-cliam-agentic-tracer")

def traced_llm_call(prompt: str, llm_function):
    """
    Traces an LLM call using the OpenTelemetry tracer initialized in the notebook.
    """
    # Ensure the global `tracer` object is accessible if not explicitly passed
    # If `tracer` is not globally available or passed, you would need to get it here:
    # tracer = trace.get_tracer("your-application-name")

    with tracer.start_as_current_span("policy_extraction_llm_call") as span:
        span.set_attribute(SpanAttributes.INPUT_VALUE, prompt)
        output = llm_function(prompt)
        span.set_attribute(SpanAttributes.OUTPUT_VALUE, output)
        return output