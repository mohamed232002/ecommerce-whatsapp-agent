
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

import time

import tools

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from .env file")

# Gemini configuration
client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(api_version="v1beta")
)

# Updated model
MODEL = "gemini-3.5-flash-lite"

SYSTEM_PROMPT = """
You are an autonomous AI shopping assistant for an e-commerce store.

You communicate in Arabic or English depending on the customer's language.

RULES:
1. Never invent product names, prices, stock, orders, or tracking information.
2. Always use the backend tools to retrieve real store information.
3. Execute multiple relevant tool calls in the same turn whenever possible.
4. Do not ask the customer to split a multi-action request into separate messages.
5. Before checkout, verify the cart and required information.
6. Never claim an operation succeeded unless the backend confirms it.
7. If a tool returns an error, explain it honestly.
8. Keep customer conversations isolated by phone number.
9. Be polite, clear, and concise.
10. Use bold formatting for prices and order numbers.
"""

# The 10 backend tools
FUNCTIONS = {
    "list_categories": tools.list_categories,
    "search_products": tools.search_products,
    "get_product_details": tools.get_product_details,
    "get_customer_cart": tools.get_customer_cart,
    "add_item_to_cart": tools.add_item_to_cart,
    "remove_cart_item": tools.remove_cart_item,
    "clear_customer_cart": tools.clear_customer_cart,
    "checkout_cart": tools.checkout_cart,
    "track_order": tools.track_order,
    "cancel_order": tools.cancel_order,
}

# Function declarations for Gemini
TOOL_DECLARATIONS = [
    types.FunctionDeclaration(
        name="list_categories",
        description="Get all available product categories.",
        parameters_json_schema={
            "type": "object",
            "properties": {}
        }
    ),
    types.FunctionDeclaration(
        name="search_products",
        description="Search products by keyword, category ID, and stock availability.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "keyword": {"type": "string"},
                "category_id": {"type": "integer"},
                "in_stock_only": {"type": "boolean"}
            },
            "required": ["keyword", "category_id", "in_stock_only"]
        }
    ),
    types.FunctionDeclaration(
        name="get_product_details",
        description="Get details of a product using its ID.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "product_id": {"type": "integer"}
            },
            "required": ["product_id"]
        }
    ),
    types.FunctionDeclaration(
        name="get_customer_cart",
        description="Get a customer's shopping cart.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "customer_name": {"type": "string"}
            },
            "required": ["customer_name"]
        }
    ),
    types.FunctionDeclaration(
        name="add_item_to_cart",
        description="Add a product to a customer's cart.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "customer_name": {"type": "string"},
                "product_id": {"type": "integer"},
                "quantity": {"type": "integer"}
            },
            "required": ["customer_name", "product_id"]
        }
    ),
    types.FunctionDeclaration(
        name="remove_cart_item",
        description="Remove an item from the cart using its item ID.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "item_id": {"type": "integer"}
            },
            "required": ["item_id"]
        }
    ),
    types.FunctionDeclaration(
        name="clear_customer_cart",
        description="Clear all items from a customer's cart.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "customer_name": {"type": "string"}
            },
            "required": ["customer_name"]
        }
    ),
    types.FunctionDeclaration(
        name="checkout_cart",
        description="Checkout a customer's cart using their shipping address.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "customer_name": {"type": "string"},
                "shipping_address": {"type": "string"}
            },
            "required": ["customer_name", "shipping_address"]
        }
    ),
    types.FunctionDeclaration(
        name="track_order",
        description="Track an order using its order ID.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "order_id": {"type": "integer"}
            },
            "required": ["order_id"]
        }
    ),
    types.FunctionDeclaration(
        name="cancel_order",
        description="Cancel an order using its order ID.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "order_id": {"type": "integer"}
            },
            "required": ["order_id"]
        }
    )
]

GEMINI_TOOLS = [
    types.Tool(function_declarations=TOOL_DECLARATIONS)
]

# Separate conversation history for each phone number
customer_sessions = {}

def generate_content_with_retry(contents, config):
    """Retry Gemini requests when the service is temporarily unavailable."""

    for attempt in range(3):
        try:
            return client.models.generate_content(
                model=MODEL,
                contents=contents,
                config=config
            )

        except Exception as error:
            error_message = str(error).upper()

            is_temporary_error = (
                "503" in error_message
                or "UNAVAILABLE" in error_message
            )

            if not is_temporary_error or attempt == 2:
                raise

            wait_seconds = 2 * (attempt + 1)

            print(
                f"Gemini temporarily unavailable. "
                f"Retrying in {wait_seconds} seconds... "
                f"(Attempt {attempt + 2}/3)"
            )

            time.sleep(wait_seconds)

def process_message(message: str, phone: str) -> str:
    """Process a customer message and execute required backend tools."""

    if phone not in customer_sessions:
        customer_sessions[phone] = []

    history = customer_sessions[phone]

    history.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=message)]
        )
    )

    try:
        # Allow multiple tool-calling rounds in one customer turn
        for _ in range(5):
            response =  generate_content_with_retry(
                contents=history,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=GEMINI_TOOLS,
                    temperature=0.2
                )
            )

            if not response.candidates:
                return "Sorry, I couldn't generate a response. Please try again."

            model_content = response.candidates[0].content
            history.append(model_content)

            function_calls = response.function_calls

            # No more tool calls: return Gemini's final answer
            if not function_calls:
                return response.text or "I couldn't generate a response."

            function_response_parts = []

            # Execute every function call returned in this round
            for function_call in function_calls:
                function_name = function_call.name
                arguments = dict(function_call.args or {})

                if function_name not in FUNCTIONS:
                    result = {
                        "success": False,
                        "error": "Unknown function"
                    }
                else:
                    try:
                        function = FUNCTIONS[function_name]
                        result = function(**arguments)
                    except Exception as error:
                        result = {
                            "success": False,
                            "error": str(error)
                        }

                function_response_parts.append(
                    types.Part.from_function_response(
                        name=function_name,
                        response={"result": result}
                    )
                )

            # Send all tool results back to Gemini together
            history.append(
                types.Content(
                    role="user",
                    parts=function_response_parts
                )
            )

        return "The request requires too many operations. Please try again."

    except Exception as error:
        print(f"Gemini Agent Error: {error}")
        return "Sorry, something went wrong while processing your request."


def reset_customer_session(phone: str):
    """Reset the conversation history for one customer."""
    customer_sessions.pop(phone, None)
