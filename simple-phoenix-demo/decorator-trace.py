from phoenix.otel import register
from openinference.instrumentation import using_attributes
from openai import OpenAI
from dotenv import load_dotenv
import os
from opentelemetry import trace 
load_dotenv()

# 🔥 Phoenix tracer (manual mode)
tracer_provider =register(
    project_name="phoenix-trace-decorator-aravind",
    auto_instrument=False,
    set_global_tracer_provider=True
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tracer = tracer_provider.get_tracer(__name__)


@tracer.chain
def run_agent(user_input: str) -> str:
    # This span is kind=CHAIN by default, captures input & output
    #user_input = "List best peaceful and happy countries to live for next 50 years and why?"
    response = call_llm(user_input)
    print('LLM response:', response)
    return response

def call_llm(prompt: str) -> str:
    with tracer.start_as_current_span("llm-completion") as span:
        span.set_attribute("openinference.span.kind", "LLM")
        span.set_attribute("input.value", prompt)
        span.set_attribute("llm.model_name", "gpt-3.5-turbo")

        result = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,)
        
        
        
        
        span.set_attribute("output.value", result.choices[0].message.content)
        span.set_attribute("llm.token_count.prompt", result.usage.prompt_tokens)
        span.set_attribute("llm.token_count.completion", result.usage.completion_tokens)
        span.set_attribute("llm.token_count.total", result.usage.total_tokens)
        span.set_status(trace.Status(trace.StatusCode.OK))
        return result.choices[0].message.content



if __name__ == "__main__":
    run_agent('List best peaceful and happy 5 countries to live for next 50 years and why? and in this 5 countires which will move down and which other countries will show  up in happiness index?')