import json
import logging
import os

from audio_utils import merge_audio_files, generate_elevenlabs_audio


output_dir = 'output/' # Where the output files will be saved

############################################
# Save the conversation to a JSON file
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
        f.write(conversation.choices[0].message.content)

############################################
# Take a conversation object and generate the audio
############################################
def generate_conversation(conversation):
    logging.info(conversation.choices[0].message.content)
    result = json.loads(conversation.choices[0].message.content)
    save_conversation(conversation)

    # Loop through the conversation object and retrieve each text
    for index, dialogue in enumerate(result["conversation"]):
        generate_elevenlabs_audio(index, dialogue["Text"], dialogue["Voice"])

    # Merge the audio files
    input_files = [os.path.join(os.getcwd(), f"{output_dir}output{i}.mp3") for i in range(len(result["conversation"]))]
    merge_audio_files(input_files, "output/output_merged.mp3")