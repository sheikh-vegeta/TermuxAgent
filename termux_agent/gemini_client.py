import os
import google.generativeai as genai

class GeminiClient:
    def __init__(self):
        """
        Initializes the Gemini client, loading the API key and system prompt.
        """
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not found.")

        genai.configure(api_key=self.api_key)

        self.system_prompt = self._load_system_prompt()
        self.model = genai.GenerativeModel('gemini-pro')

    def _load_system_prompt(self):
        """
        Loads the system prompt from prompt.md file.
        """
        try:
            with open('prompt.md', 'r') as f:
                return f.read()
        except FileNotFoundError:
            print("Warning: prompt.md not found. Continuing without a system prompt.")
            return "You are a helpful assistant."

    def send_chat_message(self, message: str, history: list = None):
        """
        Sends a message to the Gemini API and gets a response.

        Args:
            message (str): The user's message.
            history (list, optional): The conversation history. Defaults to None.

        Returns:
            str: The AI's response text.
        """
        if history is None:
            history = []

        # The chat history format for Gemini API is specific.
        # It should be a list of dictionaries with 'role' and 'parts'.
        # We prepend the system prompt to the history.
        full_history = [{'role': 'user', 'parts': [self.system_prompt]}, {'role': 'model', 'parts': ["Understood. I am ready to assist as a Termux expert."]}]
        full_history.extend(history)

        chat = self.model.start_chat(history=full_history)

        try:
            response = chat.send_message(message)
            return response.text
        except Exception as e:
            print(f"An error occurred while communicating with the Gemini API: {e}")
            return "Sorry, I encountered an error while trying to generate a response."

# Example of how to use the client (optional, for testing)
if __name__ == '__main__':
    # This requires setting the .env file and running as a script
    from dotenv import load_dotenv
    load_dotenv()

    try:
        client = GeminiClient()
        print("Gemini Client Initialized.")
        print("---")
        test_message = "How do I install git in Termux?"
        print(f"Sending test message: '{test_message}'")
        reply = client.send_chat_message(test_message)
        print(f"Received reply: {reply}")
    except ValueError as e:
        print(e)
