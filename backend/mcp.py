import json
from google.generativeai import GenerativeModel
from google.generativeai.types import ContentType

def mcp_process(model: GenerativeModel, full_prompt: str) -> dict:
    """
    Processes a prompt using the Model-Controller-Process (MCP) logic.

    Args:
        model: The configured GenerativeModel instance.
        full_prompt: The complete prompt including system instructions, context, and user input.

    Returns:
        A dictionary containing the AI's response, parsed from JSON if possible.
    """
    # For this scaffold, we'll use a simplified approach where a single prompt
    # asks the model to follow the MCP logic and return a structured JSON.
    # A more advanced implementation might have separate calls for each step.

    # Process: Generate a response based on the full prompt
    try:
        response = model.generate_content(full_prompt)

        # The prompt asks the model to return JSON, so we attempt to parse it.
        # It's important to handle cases where the output is not valid JSON.
        parsed_response = json.loads(response.text)
        return parsed_response

    except json.JSONDecodeError:
        # If the model doesn't return valid JSON, return the raw text
        # wrapped in a standard structure.
        return {
            "analysis": "Response was not valid JSON.",
            "decision": "Returning raw text.",
            "code": response.text,
            "diff": "",
            "tests": "No tests generated due to non-JSON response."
        }
    except Exception as e:
        # Handle other potential API errors
        error_text = f"An error occurred while calling the AI model: {e}"
        return {
            "analysis": "Error during generation.",
            "decision": "Aborting.",
            "code": error_text,
            "diff": "",
            "tests": ""
        }
