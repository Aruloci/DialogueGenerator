from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import requests
import logging
from audio_merger import merge_audio_files

load_dotenv()
# Set up logging
logging.basicConfig(level=logging.INFO)  # Set the logging level 

#################################################################
# Generate audio from text
#################################################################

# Function to generate audio from text
def generate_audio(text_id: int, text: str, speaker: str):
    CHUNK_SIZE = 1024
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{speaker}"

    headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": os.environ.get("ELEVENLABS_API_KEY")
    }

    data = {
    "text": text,
    "model_id": "eleven_monolingual_v1",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.5
    }
    }

    response = requests.post(url, json=data, headers=headers)
    with open(f"output{text_id}.mp3", 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

#################################################################
# Generate text based conversation
#################################################################
client = OpenAI(
  api_key=os.environ.get("OPENAI_API_KEY")
)

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  response_format={ "type": "json_object" },
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
        Did you understand that?"""
    },
    {
        "role": "user",
        "content": "Generate a dialog between two females which are talking to a male conductor about the delay of a train at the trainstation."
    }
  ]
)

logging.info(completion.choices[0].message.content)
result = json.loads(completion.choices[0].message.content)
# Save the conversation to a file
with open('conversation.json', 'w') as f:
    f.write(completion.choices[0].message.content)
# # Loop through the conversation object and retrieve each text
for index, dialogue in enumerate(result["conversation"]):
    generate_audio(index, dialogue["Text"], dialogue["Voice"])

# Merge the audio files
input_files = [
    os.path.join(os.getcwd(), "output0.mp3"),
    os.path.join(os.getcwd(), "output1.mp3"),
    os.path.join(os.getcwd(), "output2.mp3"),
    os.path.join(os.getcwd(), "output3.mp3"),
    os.path.join(os.getcwd(), "output4.mp3"),
]
merge_audio_files(input_files, "output_merged.mp3")