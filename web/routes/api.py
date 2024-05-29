import csv
import os
from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
import json
import time
import shutil

from audio_utils import generate_elevenlabs_audio
from conversation_utils import get_current_conversation_directory, get_next_conversation_directory, save_conversation, send_openai_request
from convtools import audioWriter, conversationFileReader, rttmWriter, textGridWriter
from web.routes.api_keys import get_elevenlabs_api_key, get_openai_api_key


api = Blueprint("api", __name__)

@api.route("/api/conversations", methods=["POST"])
@login_required
def create_conversation():
    start = time.time()
    
    data = request.get_json()
    user_id = current_user.id
    dialogue_prompt = data["dialoguePrompt"]
    voice_ids = data["voiceIDs"]
    openai_api_key = get_openai_api_key()
    output_dir = get_next_conversation_directory(sub_dir=f"user_{user_id}")

    # Create initial conversation with focus on dialogue content
    messages=[
        {
            "role": "system",
            "content": """You are a scriptwriter tasked with creating a highly realistic and emotionally engaging dialogue. 
            Your goal is to generate a natural conversation based on the scenario set by the user.
            To make a conversation feel more natural you should annotate every sentence with fitting emotions. 
            Speakers should also be able to interrupt or talk over each other. 
            To generate the conversation stick to the following format: 
                - Name: Name of the speaker. If no names are given generate names.
                - Text: The generated sentence for the speaker. Use ... to indicate a pause or stutter. For a longer pause use ,,,.
                Such a pause should never be longer than 2 seconds. 
                Use comic speech like "Uhm", "Hmph", "Argh" to create a more natural conversation.
                - Emotion: The corresponding emotion of the speakers sentence.
                - Timing: The time in seconds between the current and previous sentence as double. Use 0.0 if the sentence starts 
                immediately after the last one. Use any positive like 0.5 or 1.0 as double to create a small pause. A negative 
                double indicates that the sentences overlap each other. Make sure that the timing is consistent 
                with the whole conversation and feels natural.
                - Voice: The elevent labs voice id to use for the sentence. Leave this blank for now.

            To make the generated conversation easier to parse create a JSON formatted output. 
            The root of the JSON object is called "conversation". 
            Make sure the keys are named "Name", "Text", "Emotion", "Timing" and "Voice".
            One conversation should contain at least 10 sentences but should contain more.
            Did you understand that?""",
        }, 
        {
            "role": "user",
            "content": dialogue_prompt
        }
    ]
    conversation = send_openai_request(messages, openai_api_key)
    if 'error' in conversation:
        return jsonify({"message": conversation['error']}), 400
    messages.append({
        "role": "assistant",
        "content": conversation
    })

    # Optimize the timing and emotions of the conversation
    messages.append({
        "role": "user",
        "content": f"""
            Optimize the timing (pauses) and emotions of the conversation to make it sound more natural. The pauses
            should rarely be longer than 0.5 seconds. The generated pause stands for the pause to the previous dialogue.
            The conversation should feel like a real dialogue between real people. 
            Include filler words like "uhm", "uh", "you know" etc. to create a more natural conversation. 
            Adjust the dialogue where needed to make the conversation seem more natural.
            Add the voice ID from ElevenLabs. You can choose from the following IDs. Do not use any other Voice IDs.
            {voice_ids}
            Make sure to use the same voice ID for the same speaker and choose a fitting voice for the speaker.
            The voice must match the speakers name. If the speaker has a male name then choose a male voice. 
            If the name is female then choose a fitting female voice.
            Remove any ; from the generated conversation. No ; in the conversation is allowed.
            Keep the JSON format and the structure of the conversation.
            """
    })
    conversation = send_openai_request(messages, openai_api_key)
    if 'error' in conversation:
        return jsonify({"message": conversation['error']}), 400
    
    conversation = json.loads(conversation)
    for dialogue in conversation["conversation"]: # Remove any semicolons from the dialogue
        dialogue["Text"] = dialogue["Text"].replace(";", "")
    conversation = json.dumps(conversation)
    
    messages.append({
        "role": "assistant",
        "content": conversation
    })
    save_conversation(conversation, output_dir=output_dir) # Save the conversation to a JSON file
    end = time.time()
    print(f"Time taken to create conversation: {end-start:.2f} seconds")
    return jsonify({"status": "success",
                    "message": "Conversation generated successfully",
                    "conversation": conversation,
                    "conversation_history": messages})

@api.route("/api/conversations/audio", methods=["POST"])
@login_required
def create_audio():
    start = time.time()
    data = request.get_json()
    conversation = data["conversationData"]
    messages = data["conversationHistory"]
    openai_api_key = get_openai_api_key()
    elevenlabs_api_key = get_elevenlabs_api_key()
    output_dir = get_current_conversation_directory(sub_dir=f"user_{current_user.id}")
    
    # Suggest a background environment and reverb effect for the conversation
    messages.append({
        "role": "user",
        "content": """
            Based on the generated conversation suggest a background environment for the conversation. The 
            environment should match the setting of the conversation. The environment should be a fitting
            background noise to the conversation. You can choose from the following environments:
            - Restaurant
            - Train
            - Traffic
            - Quayside

            Additionally add a matching reverb effect to the conversation. You can choose from the following
            reverb effects and only those below. Choose none if no reverb effect matches the conversation:
            - Church
            - Forest
            - Sportscentre
            - Phone
            - None

            Structure the JSON output as follows:
            {
            "background_effect": "",
            "reverb_effect": ""
            }
            """
    })
    post_processing = send_openai_request(messages, openai_api_key)
    if 'error' in conversation:
        return jsonify({"message": conversation['error']}), 400
    post_processing = json.loads(post_processing)
    background_effect = post_processing["background_effect"]
    reverb_effect = post_processing["reverb_effect"]

    # Generate audio files and annotate the conversation
    audio_annotations = []
    offset = 0.0
    conversation = json.loads(conversation)
    for index, dialogue in enumerate(conversation["conversation"]):
        audio_chunk, file_name = generate_elevenlabs_audio(index, dialogue["Text"], dialogue["Voice"], dialogue["Emotion"], output_dir=output_dir, api_key=elevenlabs_api_key)
        if 'error' in audio_chunk:
            return jsonify({"message": audio_chunk['error']}), 400
        
        offset = round(offset + dialogue["Timing"], 1)
        annotations = {
            "path": "",
            "file": file_name,
            "offset": offset,
            "type": "SPEAKER",
            "subtype": "<NA>",
            "speaker": dialogue["Name"],
            "text_description": dialogue["Text"]
        }
        offset += audio_chunk.duration_seconds
        audio_annotations.append(annotations)

    # Add the background audio effect to the conversation
    if reverb_effect != "Phone":
        background_effect_annotations = {
            "path": "",
            "file": f"convtools\\ambient_noise\{background_effect}.mp3",
            "offset": 0,
            "type": "NON-SPEECH",
            "subtype": "other",
            "speaker": "<NA>",
            "text_description": f"{background_effect} background noise"
        }
        audio_annotations.append(background_effect_annotations)


    # Write the annotations to a CSV file
    csv_file_path = os.path.join(output_dir, "conversation_annotations.csv")
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
        fieldnames = ["path", "file", "offset", "type", "subtype", "speaker", "text_description"]
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for annotation in audio_annotations:
            writer.writerow(annotation) 

    # Add the reverb effect to the audio files
    conv_file = conversationFileReader.conversationFile(csv_file_path)
    aw = audioWriter.audioWriter(conv_file, output_dir)
    if reverb_effect == "Phone":
        aw.writeAudio(fileName="dialog.mp3",**{'transmission':'phone'})
    elif reverb_effect == "None":
        aw.writeAudio(fileName="dialog.mp3",**{'reverb':0.1})
    else:
        aw.writeAudio(fileName="dialog.mp3",**{'environment':reverb_effect, 'reverb':0.1})

    # write the RTTM and TextGrid files
    rw = rttmWriter.rttmWriter(conv_file, output_dir)
    rw.writeRTTM()
    tw = textGridWriter.textGridWriter(conv_file, output_dir)
    tw.writeTextGrid()

    output_dir = output_dir.replace("web\\", "")
    # Extract the conversation number
    path_parts = output_dir.split('\\')
    conversation_part = path_parts[-1]
    conversation_number = conversation_part.split('_')[-1]

    end = time.time()
    print(f"Time taken to create audio: {end-start:.2f} seconds")
    return jsonify({"status": "success",
                    "message": "Audio file generated successfully",
                    "audio_url": os.path.join(output_dir, "dialog.mp3"),
                    "conversation_number": conversation_number})

@api.route("/api/conversations/download/<int:conversation_id>", methods=["GET"])
@login_required
def download_conversation(conversation_id): 
    user_id = current_user.id
    folder_path = f"web\\static\\output\\user_{user_id}\\conversation_{conversation_id}"
    download_path = f"static\\output\\user_{user_id}\\conversation_{conversation_id}.zip"

    shutil.make_archive(folder_path, 'zip', folder_path)
    return send_file(download_path, as_attachment=True)