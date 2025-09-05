import json
from typing import Dict, Any

CONFIG_PATH = "backend/config.json"

def load_config() -> Dict[str, Any]:
    """
    Loads the configuration from the config.json file.

    Returns:
        A dictionary containing the configuration.

    Raises:
        FileNotFoundError: If the config.json file is not found.
        json.JSONDecodeError: If the config file is not valid JSON.
    """
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Configuration file not found at '{CONFIG_PATH}'.")
        print("Please copy 'backend/config.json.example' to 'backend/config.json' and fill in your API keys.")
        raise
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not parse '{CONFIG_PATH}'. Please ensure it is valid JSON.")
        raise e

# You can also add functions here to get specific config values, e.g.:
def get_api_key(service: str) -> str:
    """
    Returns the API key for a given service from the config.
    """
    config = load_config()
    return config.get("api_keys", {}).get(service)
