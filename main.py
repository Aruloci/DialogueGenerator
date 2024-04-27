import logging
import json
import csv
from dotenv import load_dotenv

from conversation_utils import send_openai_request, save_conversation
from audio_utils import generate_elevenlabs_audio
from convtools import audioWriter, conversationFileReader


# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)  # Set the logging level

messages=[
    {
        "role": "system",
        "content": """You are an expert in generating conversations based on the users requirements. Your goal is to generate a natural conversation 
        based on the scenario set by the user. To make a conversation feel more natural you should annotate every sentence with fitting emotions. Speakers
        should also be able to interrupt or talk over each other. To generate the conversation stick to the following format: 
            - Name: Name of the speaker. If no names are given generate names.
            - Text: The generated sentence for the speaker. Use ... to indicate a pause or stutter. To implement a sequence where nothing is said use '<break time="1.1s" />' like
              this: 'Hello<break time="0.8s" />. How are you?' The number in the break tag indicates the length of the pause in seconds.
              Such a pause should never be longer than 2 seconds. Use comic speech like "Uhm", "Hmph", "Argh" to create a more natural conversation.
            - Emotion: The corresponding emotion of the speakers sentence.
            - Timing: The time in seconds between the current and previous sentence as double. Use 0.0 if the sentence starts immediately after the last one. Use any positive like 0.5 or 1.0 as
            double to create a small pause. A negative double indicates that the sentences overlap each other. Make sure that the timing is consistent with the whole conversation and feels natural.
            - Voice: The elevent labs voice id to use for the sentence. Leave this blank for now.

        To make the generated conversation easier to parse create a JSON formatted output. The root of the JSON object is called "conversation". Make sure the keys are named "Name", "Text", "Emotion", "Timing" and "Voice".
        One conversation should contain at least 10 sentences but should contain more.
        Did you understand that?""",
    }, 
    {
        "role": "user",
        # "content": "Generate a dialog between two females which are talking to a male conductor about the delay of a train at the trainstation.",
        # "content": "Generate a dialog between a boss and his employee about his bad performance at work.",
        "content": "Generate a dialog between an interviewer and an old WW2 veteran talking about his experience.",
    }
]

# Create initial conversation with focus on dialogue content
conversation = send_openai_request(messages)
messages.append({
    "role": "assistant",
    "content": conversation
})

# Optimize the timing and emotions of the conversation
messages.append({
    "role": "user",
    "content": """
        Optimize the timing (pauses) and emotions of the conversation to make it sound more natural. The pauses
        should rarely be longer than 1 second. The conversation should feel like a real dialogue 
        between real people. Besides the timing add the voice ID from ElevenLabs. You can choose from the following IDs:
        - NOpBlnGInO9m6vDvFkFC : Old Male with American accent
        - Mr0lS24b2pkDEz6noGEd : Young Female with American accent
        - otVgZoZFXk2SZDc0eBdZ : Young Female with Australian accent
        - WLKp2jV6nrS8aMkPPDRO : Middle-aged Male with Australian accent
        - x3gYeuNB0kLLYxOZsaSh : Middle-aged Male with Indian accent
        - aTxZrSrp47xsP6Ot4Kgd : Young Female with African American accent
        Make sure to use the same voice ID for the same speaker.
        Keep the JSON format and the structure of the conversation.
        """
})
conversation = send_openai_request(messages)

# # Generate conversation and process audio files
# create_audio_file(conversation)

save_conversation(conversation)

# Generate audio files and annotate the conversation
audio_chunks = []
audio_annotations = []
offset = 0.0
conversation = json.loads(conversation)
for index, dialogue in enumerate(conversation["conversation"]):
    audio_chunk, file_name = generate_elevenlabs_audio(index, dialogue["Text"], dialogue["Voice"], dialogue["Timing"], dialogue["Emotion"])
    
    annotations = {
        "path": "",
        "file": file_name,
        "offset": offset,
        "type": "SPEAKER",
        "subtype": "<NA>",
        "speaker": dialogue["Name"],
        "text_description": dialogue["Text"]
    }
    offset += round(audio_chunk.duration_seconds,1)
    audio_annotations.append(annotations)
    # audio_chunks.append(audio_chunk)
# merge_audio_files(audio_chunks, "output/output_merged.mp3")

# Write the annotations to a CSV file
csv_file_path = "conversation_annotations.csv"
with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
    fieldnames = ["path", "file", "offset", "type", "subtype", "speaker", "text_description"]
    writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=";")
    writer.writeheader()
    for annotation in audio_annotations:
        writer.writerow(annotation) 

cf = conversationFileReader.conversationFile("conversation_annotations.csv")
aw = audioWriter.audioWriter(cf,"output\\")
aw.writeAudio(fileName="dialog-1-reverb.mp3",**{'reverb':0.1})
aw.writeAudio(fileName="dialog-1-church.mp3",**{'environment':'church'})
aw.writeAudio(fileName="dialog-1-phone.mp3",**{'transmission':'phone'})
aw.writeAudio(fileName="dialog-1-bitrate.mp3",**{'bitrate':4})
aw.writeAudio(fileName="dialog-1-clipping.mp3",**{'clipping':-16})
aw.writeAudio(fileName="dialog-1-multiEffect.mp3",**{'environment':'sportscentre', 'clipping':-16, 'transmission':'phone'})