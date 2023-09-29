import openai
import json
from database import DatabaseManager
from config.settings import OPENAI_API_KEY
from utils.utils import scene_to_text


class named_entity_recognizer:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY
        self.db_manager = DatabaseManager()

    def identify_named_entities(self, text: str):
        """Identify named entities in a given text."""

        # Prepare function descriptions for OpenAI API call
        functions = [
            {
                "name": "update_character_descriptors",
                "description": "Update the character descriptors in the database.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "descriptors": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["name", "descriptors", "scene"]
                }
            }
        ]

        # Prepare messages for OpenAI API call
        messages = [
            {"role": "system", "content": "You are a helpful assistant for identifying named entities. only respond with defined functions."},
            {"role": "user", "content": f"Identify the characters and scenes in the following text: {text}"}
        ]

        current_scene = self.db_manager.get_current_scene()

        # If a current scene is provided, include it in the messages to provide context to the model
        if current_scene:
            messages.append({"role": "system", "content": f"The most recent scene object is: {scene_to_text(current_scene)}"})

        # Make OpenAI API call
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=messages,
            functions=functions,
        )

        # Process the response
        response_message = response["choices"][0]["message"]

        if response_message.get("function_call"):
            function_name = response_message["function_call"]["name"]
            function_args = json.loads(response_message["function_call"]["arguments"])

            if function_name == "update_character_descriptors":
                return self.db_manager.update_character_descriptors(**function_args)

if __name__ == "__main__":
    text_sample = "In a dark and stormy night, Arthur and Merlin were devising a plan in the grand hall."
    named_entity_recognizer.identify_named_entities(text_sample)
