import logging
import os

from dotenv import load_dotenv
from openai import OpenAI
from conversation_utils import generate_conversation


# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)  # Set the logging level

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Generate conversation and process audio files
conversation = client.chat.completions.create(
    model="gpt-3.5-turbo",
    response_format={"type": "json_object"},
    messages=[
        {
            "role": "system",
            "content": """You are an expert in generating conversations based on the users requirements. Your goal is to generate a natural conversation 
            based on the scenario set by the user. To make a conversation feel more natural you should annotate every sentence with fitting emotions. Speakers
            should also be able to interrupt or talk over each other. To generate the conversation stick to the following format: 
                - Name: Name of the speaker. If no names are given generate names.
                - Text: The generated sentence for the speaker.
                - Emotion: The corresponding emotion of the speakers sentence.
                - Timing: The time in seconds between the current and previous sentence. Use 0 if the sentence starts immediately after the last one. Use any positive
                number to create a small waiting window. A negative number indicates that the sentences overlap each other.
                - Voice: The elevent labs voice id to use for the sentence. Use "H1oKRJV3pAGTo5Un0uwG" for male speakers and "Mr0lS24b2pkDEz6noGEd" or "otVgZoZFXk2SZDc0eBdZ" for female speakers. If there are
                multiple female speakers choose one voice for each of them. The voice should be the same for the same speaker throughout the conversation. Make sure that no voice is used for multiple speakers.

            To make the generated conversation easier to parse create a JSON formatted output. The root of the JSON object is called "conversation". Make sure the keys are named "Name", "Text", "Emotion", "Timing" and "Voice".
            One conversation should contain at least 5 sentences.
            Did you understand that?""",
        },
        {
            "role": "user",
            "content": "Generate a dialog between two females which are talking to a male conductor about the delay of a train at the trainstation.",
        },
    ],
)

# Generate conversation and process audio files
generate_conversation(conversation)