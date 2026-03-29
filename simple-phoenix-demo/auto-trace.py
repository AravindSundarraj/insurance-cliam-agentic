from phoenix.otel import register
from openinference.instrumentation import using_attributes
from openai import OpenAI
from dotenv import load_dotenv
import os
from opentelemetry import trace
import json
from openinference.semconv.trace import SpanAttributes, OpenInferenceSpanKindValues
from opentelemetry.trace import Status, StatusCode
from openinference.instrumentation import using_prompt_template
load_dotenv()

tracer_provider = register(
    project_name="customer-support-agentic-trace",
    auto_instrument=False,
    set_global_tracer_provider=True
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tracer = tracer_provider.get_tracer(__name__)

from openinference.instrumentation.openai import OpenAIInstrumentor
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

tools = [
    {
        "type": "function",
        "function": {
            "name": "product_search",
            "description": "Search for products based on criteria.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query string."},
                    "category": {"type": "string", "description": "The category to filter the search."},
                    "min_price": {"type": "number", "description": "The minimum price.", "default": 0},
                    "max_price": {"type": "number", "description": "The maximum price."},
                    "page": {"type": "integer", "description": "The page number.", "default": 1},
                    "page_size": {"type": "integer", "description": "Results per page.", "default": 20},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "track_package",
            "description": "Track the status of a package based on the tracking number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tracking_number": {"type": "integer", "description": "The tracking number."}
                },
                "required": ["tracking_number"],
            }
        }
    }
]


def product_search(query, category=None, page=1, page_size=5):
    products = [
        {"name": "Energy Star Refrigerator", "category": "home office", "price": 899},
        {"name": "LED Desk Lamp", "category": "home office", "price": 45},
        {"name": "Solar Powered Charger", "category": "home office", "price": 35},
        {"name": "Smart Thermostat", "category": "home office", "price": 199},
        {"name": "Energy Efficient Monitor", "category": "home office", "price": 350},
    ]
    if category:
        products = [p for p in products if p["category"] == category]
    products = [p for p in products if query.lower() in p["name"].lower()]
    start = (page - 1) * page_size
    return products[start:start + page_size]


def run_prompt(input):
    with using_attributes(session_id="my-session-id-2", user_id="user-456"):
        with tracer.start_as_current_span("agent-flow") as parent_span:
            parent_span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, OpenInferenceSpanKindValues.CHAIN.value)
            parent_span.set_attribute(SpanAttributes.INPUT_VALUE, input)
            parent_span.add_event("LLM decides which tool to use based on the input and available tools.")

            # Step 1: LLM decides tool
            messages = [
                {"role": "system", "content": "You are a helpful customer support agent..."},
                {"role": "user", "content": input},
            ]

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                tools=tools,
                tool_choice="required",
                messages=messages,
            )

            tool_call = response.choices[0].message.tool_calls[0]

            # Step 2: Execute tool
            if tool_call.function.name == "product_search":
                args = json.loads(tool_call.function.arguments)
                with tracer.start_as_current_span("product_search") as tool_span:
                    tool_span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, OpenInferenceSpanKindValues.TOOL.value)
                    tool_span.set_attribute(SpanAttributes.TOOL_NAME, tool_call.function.name)
                    tool_span.set_attribute(SpanAttributes.INPUT_VALUE, json.dumps(args))
                    result = product_search(**args)
                    tool_span.set_attribute(SpanAttributes.OUTPUT_VALUE, json.dumps(result))
                    tool_span.set_attribute(SpanAttributes.TOOL_PARAMETERS, json.dumps(args))

            # Step 3: Send back to LLM
            messages.append(response.choices[0].message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            })

            final_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
            )
            parent_span.set_attribute(SpanAttributes.OUTPUT_VALUE, final_response.choices[0].message.content)
            parent_span.set_status(Status(status_code=StatusCode.OK))


run_prompt("I'm interested in energy-efficient appliances, but I'm not sure which ones are best for a small home office. Can you help?")