"""
STRUCTURED OUTPUT WITH TOOL USE - Practice File 01
==================================================

This file teaches how to:
1. Define JSON schemas for predictable outputs
2. Use type specifications and validation
3. Distinguish required vs optional fields
4. Implement enum usage for controlled values
5. Format tool outputs correctly
6. Handle nested object structures
7. Create arrays and lists properly
8. Handle errors in structured output

REAL-WORLD SCENARIO:
You are building an order processing system that extracts
order details from user messages and returns structured data
that other systems can consume.
"""

import os
import json
import re
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
from anthropic import Anthropic

# ============================================================================
# SECTION 1: SETUP AND ENVIRONMENT
# ============================================================================

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file")

client = Anthropic()

# ============================================================================
# SECTION 2: DEFINING OUTPUT SCHEMAS WITH PYDANTIC
# ============================================================================
# Pydantic provides automatic validation and clear schema definition

# Example 1: Simple order extraction schema
class OrderStatus(Enum):
    """Controlled values for order status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItem(BaseModel):
    """A single item in an order."""
    product_id: str = Field(description="Unique product identifier")
    product_name: str = Field(description="Name of the product")
    quantity: int = Field(ge=1, description="Number of items ordered")
    unit_price: float = Field(gt=0, description="Price per unit in USD")
    # Optional fields - default values handled gracefully
    discount: Optional[float] = Field(default=0.0, ge=0, le=1,
                                      description="Discount percentage (0-1)")
    notes: Optional[str] = Field(default=None, description="Special instructions")

    @field_validator('product_id')
    @classmethod
    def validate_product_id(cls, v: str) -> str:
        """Ensure product ID follows expected format."""
        if not re.match(r'^[A-Z]{2,3}-\d{4,6}$', v):
            raise ValueError(
                f"Product ID must be format XX-9999 or XXX-999999, got: {v}"
            )
        return v


class CustomerInfo(BaseModel):
    """Customer information for an order."""
    customer_id: Optional[str] = Field(
        default=None,
        description="Customer identifier if known"
    )
    name: str = Field(description="Customer full name")
    email: str = Field(description="Customer email address")
    phone: Optional[str] = Field(default=None, description="Contact phone")
    # Nested address object
    shipping_address: Dict[str, str] = Field(
        description="Shipping address components",
        default_factory=dict
    )

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Basic email validation."""
        if '@' not in v or '.' not in v.split('@')[1]:
            raise ValueError(f"Invalid email format: {v}")
        return v.lower()


class OrderSchema(BaseModel):
    """Complete order structure with validation."""
    order_id: str = Field(description="Unique order identifier")
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    customer: CustomerInfo = Field(description="Customer details")
    items: List[OrderItem] = Field(min_length=1, description="Ordered items")
    shipping_method: str = Field(description="Shipping option selected")
    total_amount: float = Field(gt=0, description="Total order amount")
    notes: Optional[str] = Field(default=None)

    @field_validator('items')
    @classmethod
    def validate_items_not_empty(cls, v: List[OrderItem]) -> List[OrderItem]:
        """Ensure order has at least one item."""
        if not v:
            raise ValueError("Order must have at least one item")
        return v

    @field_validator('shipping_method')
    @classmethod
    def validate_shipping_method(cls, v: str) -> str:
        """Validate shipping method against allowed values."""
        allowed = ['standard', 'express', 'overnight', 'pickup']
        if v.lower() not in allowed:
            raise ValueError(
                f"Shipping method must be one of: {', '.join(allowed)}"
            )
        return v.lower()

    def calculate_total(self) -> float:
        """Recalculate total from items for validation."""
        subtotal = sum(
            item.quantity * item.unit_price * (1 - item.discount)
            for item in self.items
        )
        shipping_costs = {'standard': 5.99, 'express': 12.99,
                          'overnight': 24.99, 'pickup': 0}
        shipping = shipping_costs.get(self.shipping_method, 0)
        return round(subtotal + shipping, 2)


# ============================================================================
# SECTION 3: TOOL OUTPUT FORMAT SPECIFICATIONS
# ============================================================================
# Claude tools use JSON schema for output formatting

def create_extraction_tool_schema() -> Dict[str, Any]:
    """
    Create a JSON schema for an information extraction tool.

    This schema defines how the LLM should format its tool output
    when extracting structured data from unstructured text.
    """
    return {
        "name": "order_extraction",
        "description": "Extracts order details from customer messages",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_summary": {
                    "type": "string",
                    "description": "Concise summary of the order"
                },
                "customer_details": {
                    "type": "object",
                    "description": "Extracted customer information",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"}
                    },
                    "required": ["name", "email"]
                },
                "products": {
                    "type": "array",
                    "description": "List of products ordered",
                    "items": {
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "string"},
                            "quantity": {"type": "integer", "minimum": 1},
                            "unit_price": {"type": "number", "minimum": 0}
                        },
                        "required": ["product_id", "quantity"]
                    }
                },
                "confidence": {
                    "type": "number",
                    "description": "Confidence score 0-1",
                    "minimum": 0,
                    "maximum": 1
                },
                "missing_information": {
                    "type": "array",
                    "description": "Fields that could not be extracted",
                    "items": {"type": "string"}
                }
            },
            "required": ["order_summary", "customer_details", "products"]
        }
    }


# ============================================================================
# SECTION 4: USING TOOLS WITH STRUCTURED OUTPUT
# ============================================================================

def extract_order_with_tools(customer_message: str) -> Dict[str, Any]:
    """
    Extract order information using Claude tools with structured output.

    Args:
        customer_message: Raw customer order message

    Returns:
        Structured order data conforming to schema
    """
    # System prompt with explicit schema requirements
    system_prompt = """
You are an order processing assistant. Your job is to extract
structured order information from customer messages.

IMPORTANT OUTPUT RULES:
1. ALWAYS respond with a valid JSON object matching this schema:
{
  "order_summary": "<2-3 sentence summary>",
  "customer_details": {
    "name": "<extracted name or null>",
    "email": "<extracted email or null>",
    "phone": "<extracted phone or null>"
  },
  "products": [
    {
      "product_id": "<product identifier or null>",
      "quantity": <number>,
      "unit_price": <number or null>
    }
  ],
  "confidence": <0.0 to 1.0>,
  "missing_information": ["<list of fields not found>"]
}

2. NEVER add extra fields not in the schema
3. NEVER wrap the JSON in markdown or code blocks
4. Use null for missing or unknown values
5. confidence should reflect how certain you are:
   - 0.9-1.0: All fields extracted with high confidence
   - 0.7-0.9: Most fields extracted, some uncertain
   - 0.5-0.7: Partial extraction, significant uncertainty
   - Below 0.5: Major missing information

3. List missing_information only for required schema fields
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20250601",
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {"role": "user", "content": customer_message}
        ]
    )

    # Parse the JSON response
    raw_output = response.content[0].text.strip()

    # Handle potential markdown code blocks
    if raw_output.startswith('```'):
        # Remove code block markers
        lines = raw_output.split('\n')
        raw_output = '\n'.join(lines[1:-1])  # Remove first and last line

    try:
        structured_data = json.loads(raw_output)
        return structured_data
    except json.JSONDecodeError as e:
        return {
            "error": "Failed to parse structured output",
            "raw_response": raw_output,
            "parse_error": str(e)
        }


# ============================================================================
# SECTION 5: VALIDATING STRUCTURED OUTPUT
# ============================================================================

def validate_structured_output(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate that structured output meets schema requirements.

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check required top-level fields
    required_fields = ['order_summary', 'customer_details', 'products']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Validate customer_details structure
    if 'customer_details' in data:
        customer = data['customer_details']
        if not isinstance(customer, dict):
            errors.append("customer_details must be an object")
        else:
            if 'name' not in customer:
                errors.append("customer_details.name is required")
            if 'email' not in customer:
                errors.append("customer_details.email is required")

    # Validate products array
    if 'products' in data:
        if not isinstance(data['products'], list):
            errors.append("products must be an array")
        elif len(data['products']) == 0:
            errors.append("products array cannot be empty")
        else:
            for i, product in enumerate(data['products']):
                if not isinstance(product, dict):
                    errors.append(f"products[{i}] must be an object")
                elif 'quantity' not in product:
                    errors.append(f"products[{i}].quantity is required")

    # Validate confidence score
    if 'confidence' in data:
        conf = data['confidence']
        if not isinstance(conf, (int, float)) or conf < 0 or conf > 1:
            errors.append("confidence must be a number between 0 and 1")

    return (len(errors) == 0, errors)


# ============================================================================
# SECTION 6: NESTED OBJECT HANDLING
# ============================================================================

class NestedSchemaExample:
    """
    Example of deeply nested object schemas and validation.
    """

    @staticmethod
    def create_nested_schema() -> Dict[str, Any]:
        """Create a schema for complex nested data."""
        return {
            "type": "object",
            "properties": {
                "company": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "departments": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "teams": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": {"type": "string"},
                                                "members": {
                                                    "type": "array",
                                                    "items": {"type": "string"}
                                                }
                                            },
                                            "required": ["name"]
                                        }
                                    }
                                },
                                "required": ["name"]
                            }
                        }
                    },
                    "required": ["name", "departments"]
                }
            },
            "required": ["company"]
        }

    @staticmethod
    def validate_nested_structure(data: Dict, path: str = "") -> List[str]:
        """Recursively validate nested structures."""
        errors = []

        if not isinstance(data, dict):
            return errors

        # Check for required fields at each level
        if 'company' in data:
            company = data['company']
            if not isinstance(company, dict):
                errors.append(f"{path}company must be an object")
            else:
                if 'name' not in company:
                    errors.append(f"{path}company.name is required")
                if 'departments' in company:
                    if not isinstance(company['departments'], list):
                        errors.append(f"{path}company.departments must be an array")

        return errors


# ============================================================================
# SECTION 7: ERROR HANDLING IN STRUCTURED OUTPUT
# ============================================================================

class StructuredOutputError(Exception):
    """Custom exception for structured output errors."""

    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.errors = errors or []


def parse_with_error_handling(raw_output: str) -> Optional[Dict]:
    """
    Parse JSON output with comprehensive error handling.

    Args:
        raw_output: Raw JSON string from LLM

    Returns:
        Parsed dictionary or None if parsing fails

    Raises:
        StructuredOutputError: When parsing or validation fails
    """
    errors = []

    # Step 1: Clean the output
    cleaned = raw_output.strip()

    # Remove markdown code blocks if present
    if cleaned.startswith('```json'):
        cleaned = cleaned[7:]
    elif cleaned.startswith('```'):
        cleaned = cleaned[3:]
    if cleaned.endswith('```'):
        cleaned = cleaned[:-3]

    # Step 2: Try parsing
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        # Attempt recovery strategies
        # Strategy 1: Fix trailing comma
        cleaned_fixed = re.sub(r',\s*}', '}', cleaned)
        cleaned_fixed = re.sub(r',\s*]', ']', cleaned_fixed)

        try:
            data = json.loads(cleaned_fixed)
        except json.JSONDecodeError:
            # Strategy 2: Find JSON object boundaries
            match = re.search(r'\{[\s\S]*\}', cleaned)
            if match:
                try:
                    data = json.loads(match.group())
                except json.JSONDecodeError:
                    errors.append(f"JSON parse error: {e}")
                    errors.append(f"Attempted cleanups: trailing commas")
                    raise StructuredOutputError(
                        "Failed to parse JSON output",
                        errors
                    )

    # Step 3: Validate structure
    is_valid, validation_errors = validate_structured_output(data)
    if not is_valid:
        raise StructuredOutputError(
            "Output validation failed",
            validation_errors
        )

    return data


# ============================================================================
# SECTION 8: EXAMPLE USAGE AND DEMONSTRATION
# ============================================================================

def demonstrate_structured_output():
    """Demonstrate structured output patterns."""

    print("=" * 60)
    print("STRUCTURED OUTPUT - PRACTICE 01: OUTPUT SCHEMAS")
    print("=" * 60)

    # Demonstrate schema creation
    print("\n[DEMO] Creating extraction tool schema...")
    schema = create_extraction_tool_schema()
    print(f"Schema name: {schema['name']}")
    print(f"Required fields: {list(schema['input_schema']['properties'].keys())}")

    # Demonstrate validation
    print("\n[DEMO] Validating structured output...")
    test_data = {
        "order_summary": "Customer ordered 3 items",
        "customer_details": {
            "name": "John Doe",
            "email": "john@example.com"
        },
        "products": [
            {"product_id": "TB-1234", "quantity": 2}
        ],
        "confidence": 0.85
    }
    is_valid, errors = validate_structured_output(test_data)
    print(f"Valid: {is_valid}")
    if errors:
        print(f"Errors: {errors}")

    # Demonstrate error handling
    print("\n[DEMO] Error handling in structured output...")
    invalid_json = '{"name": "test", "items": [1, 2, 3,]}'
    try:
        parse_with_error_handling(invalid_json)
    except StructuredOutputError as e:
        print(f"Caught error: {e}")
        print(f"Details: {e.errors}")

    print("\n" + "=" * 60)
    print("WHAT WE HAVE LEARNT:")
    print("=" * 60)
    print("""
1. JSON SCHEMA DEFINITION
   - Define object structure with typed fields
   - Specify required vs optional fields
   - Use enums for controlled value sets
   - Nest objects for complex data

2. VALIDATION WITH PYDANTIC
   - Use Field() for descriptions and constraints
   - Add validators for custom logic
   - Use enums for string restrictions
   - Handle optional fields with defaults

3. TOOL OUTPUT FORMATTING
   - Always respond with valid JSON
   - Match exact schema structure
   - Use null for missing values
   - Include confidence scores

4. ERROR HANDLING
   - Clean markdown code blocks
   - Fix common JSON errors (trailing commas)
   - Validate structure after parsing
   - Provide detailed error messages

5. COMMON MISTAKES TO AVOID
   - Missing required fields
   - Wrong types for values
   - Not handling null/missing gracefully
   - Forgetting array minLength
   - Not validating enums

6. BEST PRACTICES
   - Keep schemas as simple as possible
   - Use descriptive field names
   - Document field meanings in descriptions
   - Test with edge cases
   - Include confidence scores for uncertain extractions
""")


if __name__ == "__main__":
    demonstrate_structured_output()


# ============================================================================
# INTERVIEW Q&A PREP
# ============================================================================
"""
Q: How do you ensure LLM outputs match a specific schema?
A: Include the exact JSON schema in the system prompt with clear
   formatting rules. Validate the output and retry if it doesn't
   match. Use examples of valid output.

Q: What is the difference between required and optional fields?
A: Required fields must be present for the output to be valid.
   Optional fields can be null or omitted. Always specify which
   fields are required in your schema.

Q: How do you handle nested structures in tool outputs?
A: Define nested schemas recursively, validate each level separately,
   and provide clear error messages that indicate which level failed.

Q: Why use enums instead of free-form strings?
A: Enums restrict possible values, making validation easier and
   preventing unexpected outputs. They also serve as documentation
   of allowed values.
"""