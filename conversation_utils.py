import datetime
import json
import logging
import os

from openai import OpenAI
import pandas as pd
from audio_utils import merge_audio_files, generate_elevenlabs_audio


############################################
# Save the conversation text to a JSON file
############################################
def save_conversation(conversation, output_dir="output"):
    # Create a new directory for the conversation
    os.makedirs(output_dir)

    # Write the generated conversation to the file
    filename = os.path.join(output_dir, "conversation.json")
    with open(filename, 'w') as f:
        f.write(conversation)

############################################
# Take a conversation object and generate the audio
############################################
def create_audio_file(conversation):
    audio_chunks = []
    logging.info(conversation)
    result = json.loads(conversation)
    save_conversation(conversation)

    # Loop through the conversation object and generate audio files
    for index, dialogue in enumerate(result["conversation"]):
        audio_chunks.append(generate_elevenlabs_audio(index, dialogue["Text"], dialogue["Voice"], dialogue["Timing"], dialogue["Emotion"]))
        # generate_elevenlabs_audio(index, dialogue["Text"], dialogue["Voice"], dialogue["Timing"], dialogue["Emotion"])

    # Merge the audio files
    # input_files = [os.path.join(os.getcwd(), f"{output_dir}output{i}.mp3") for i in range(len(result["conversation"]))]
    merge_audio_files(audio_chunks, "output/output_merged.mp3")
    print("Conversation audio generated and saved to output/output_merged.mp3")

############################################
# Send a request to the OpenAI API
# Documentation: https://platform.openai.com/docs/guides/text-generation
############################################
def send_openai_request(messages, api_key=os.environ.get("OPENAI_API_KEY")):
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        response_format={"type": "json_object"},
        messages=messages
    )
    return response.choices[0].message.content

############################################
# Get next available conversation directory
############################################
def get_next_conversation_directory(sub_dir="user"):
    # Create the user directory if it doesn't exist
    output_dir = os.path.join("output", sub_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Find the next available directory
    existing_directories = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
    existing_directories.sort(key=lambda x: int(x.split("_")[-1]))
    if existing_directories:
        last_directory = existing_directories[-1]
        next_directory_number = int(last_directory.split("_")[-1]) + 1
    else:
        next_directory_number = 1  # Start with conversation_1 if no directories exist yet
    
    return os.path.join(output_dir, f"conversation_{next_directory_number}")

############################################
# Get the current conversation directory
############################################
def get_current_conversation_directory(sub_dir="user"):
    output_dir = os.path.join("output", sub_dir)

    # Find the current conversation directory
    existing_directories = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
    existing_directories.sort(key=lambda x: int(x.split("_")[-1]))
    if existing_directories:
        current_directory = existing_directories[-1]
    else:
        current_directory = get_next_conversation_directory(sub_dir)
    
    return os.path.join(output_dir, current_directory)
 
    