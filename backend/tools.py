import asyncio
from functools import partial
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Any

from config import load_config

def format_search_results(results: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Formats the raw Google API search results into a cleaner list.
    """
    formatted = []
    if "items" in results:
        for item in results["items"]:
            formatted.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet"),
            })
    return formatted

async def google_search(query: str, num_results: int = 5) -> Dict[str, Any]:
    """
    Performs a Google search using the Custom Search API and returns formatted results.

    Args:
        query: The search query string.
        num_results: The number of results to return.

    Returns:
        A dictionary containing the status and either the results or an error message.
    """
    try:
        config = load_config()
        api_key = config.get("api_keys", {}).get("google_api_key")
        cse_id = config.get("api_keys", {}).get("google_cse_id")

        if not api_key or "YOUR_GOOGLE_API_KEY" in api_key:
            return {"status": "error", "message": "Google API key is not configured in config.json."}
        if not cse_id or "YOUR_GOOGLE_CSE_ID" in cse_id:
            return {"status": "error", "message": "Google CSE ID is not configured in config.json."}

        # The Google API client is synchronous, so we run it in an executor
        # to avoid blocking the asyncio event loop.
        loop = asyncio.get_running_loop()

        # partial is used to pass arguments to the sync function in the executor
        sync_search_call = partial(
            build("customsearch", "v1", developerKey=api_key).cse().list(q=query, cx=cse_id, num=num_results).execute
        )

        print(f"Performing Google search for: '{query}'")
        results = await loop.run_in_executor(None, sync_search_call)

        formatted_results = format_search_results(results)
        print(f"Found {len(formatted_results)} results.")

        return {"status": "success", "results": formatted_results}

    except FileNotFoundError:
        return {"status": "error", "message": "Configuration file not found."}
    except HttpError as e:
        error_message = f"An HTTP error occurred during Google search: {e.content.decode()}"
        print(error_message)
        return {"status": "error", "message": error_message}
    except Exception as e:
        error_message = f"An unexpected error occurred during Google search: {e}"
        print(error_message)
        return {"status": "error", "message": error_message}

# Example usage (for testing this file directly)
if __name__ == "__main__":
    async def main():
        search_query = "What are the latest trends in AI?"
        results = await google_search(search_query)
        import json
        print(json.dumps(results, indent=2))

    asyncio.run(main())
