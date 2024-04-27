import json
import logging
import os

from openai import OpenAI
import pandas as pd
from audio_utils import merge_audio_files, generate_elevenlabs_audio


# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

output_dir = 'output/' # Where the output files will be saved

############################################
# Save the conversation text to a JSON file
############################################
def save_conversation(conversation):
    base_filename = 'conversation.json'
    conv_dir = os.path.join(output_dir, 'conversation')

    # Find the next available filename
    conv_counter = 1
    while True:
        filename = os.path.join(conv_dir, base_filename)
        if conv_counter > 1:
            filename = os.path.join(conv_dir, f'conversation{conv_counter}.json')
        if os.path.exists(filename):
            conv_counter += 1
        else:
            break

    # Write the generated conversation to the file
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
def send_openai_request(messages):
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        response_format={"type": "json_object"},
        messages=messages
    )
    return response.choices[0].message.content

############################################
# Convert conversation JSON to CSV and adjust fields to fit convTools
############################################
def convert_json_to_csv(conversation):
    df = pd.DataFrame(conversation['conversation'])
    df.to_csv("output/conversation/conversation60.csv",index=False, sep=";")
    