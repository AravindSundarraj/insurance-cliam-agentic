from phoenix.otel import register
from openinference.instrumentation import using_attributes
from openai import OpenAI
from dotenv import load_dotenv
import os
from opentelemetry import trace   # 🔥 REQUIRED for manual spans

load_dotenv()

# 🔥 Phoenix tracer
tracer_provider = register(
    project_name="phoenix-tracing-demo-aravind",
    auto_instrument=False,
    set_global_tracer_provider=True
)

# 🔥 manual tracer
tracer = trace.get_tracer(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def main():

    with using_attributes(
        session_id="demo-session",
        user_id="aravind",
        metadata={"project": "phoenix-tracing-demo-aravind"}
    ):

        # 🔥 MANUAL SPAN (this is what was missing)
        with tracer.start_as_current_span("openai-response-span") as span:

            response = client.responses.create(
                model="gpt-4.1-mini",
                input="Explain tracing in simple terms"
            )

            # optional enrichment
            span.set_attribute("model", "gpt-4.1-mini")

            print(response.output[0].content[0].text)

if __name__ == "__main__":
    main()