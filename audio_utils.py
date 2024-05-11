import os
import requests
from io import BytesIO

import logging
from pydub import AudioSegment
from pydub.silence import detect_nonsilent, detect_silence


############################################
# Text to speech using the Eleven Labs API
############################################
def generate_elevenlabs_audio(text_id: int, text: str, speaker: str, timing: int, emotion: str = "neutral", output_dir: str = "output/"):
    CHUNK_SIZE = 1024
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{speaker}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": os.environ.get("ELEVENLABS_API_KEY")
    }
    data = {
        "text": f'{text},,,,,,.<break time="4.0s" />he said {emotion}ly.',
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        audio_buffer = BytesIO()

        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                audio_buffer.write(chunk)
        audio_buffer.seek(0) # Reset the buffer position to the beginning
        audio_segment = AudioSegment.from_file(audio_buffer, format="mp3")

        audio_segment = clip_audio_at_pause2(audio_segment) # Clip audio at pause to remove "he said" part
        # audio_segment = add_pause(audio_segment, pause_duration=timing * 1000) # Add a pause at the end of the audio
        file_name = os.path.join(output_dir, f"output{text_id}.mp3")
        audio_segment.export(file_name, format="mp3") # Save the audio file
        return audio_segment, file_name
    else:
        logging.error(f"Failed to fetch audio for text_id={text_id}: {response.status_code} {response.reason}")
        return None, None 

############################################
# Merge multiple audio files into one
############################################
def merge_audio_files(audio_chunks, output_file):
    # Initialize an empty audio segment
    merged_audio = AudioSegment.empty()

    # Iterate over each audio chunk and concatenate them
    for chunk in audio_chunks:
        merged_audio += chunk

    # Save the concatenated audio file
    merged_audio.export(output_file, format="mp3")

############################################
# Clip audio when a pause is detected using detect_nonsilent
############################################
def clip_audio_at_pause(audio, min_silence_len=2000, silence_thresh=-80):

    # Detect non-silent chunks
    pause_detected = False
    loop_limit = 10
    loop_count = 0
    nonsilent_chunks = []

    while not pause_detected and loop_count < loop_limit:
        nonsilent_chunks = detect_nonsilent(
            audio,
            min_silence_len=min_silence_len,
            silence_thresh=silence_thresh
        )
        if len(nonsilent_chunks) > 1:
            pause_detected = True
        loop_count += 1
        silence_thresh += 7 # Increase the silence threshold for each loop

    if pause_detected:
        # Calculate the end of speech by adding pause_extension to the end of the first non-silent chunk
        nonsilent_chunks[0][1] += 150
        end_of_speech = nonsilent_chunks[0][1]
        clipped_audio = audio[:end_of_speech]
        return clipped_audio
    else:
        # Log a warning and return the original audio if no pauses are detected
        logging.warning("Could not detect a pause in the audio. Returning the original audio.")
        return audio
    
############################################
# Clip audio when a pause is detected using detect_silence
############################################
def clip_audio_at_pause2(audio, min_silence_len=2000, silence_thresh=-80):

    # Detect non-silent chunks
    pause_detected = False
    loop_limit = 10
    loop_count = 0
    nonsilent_chunks = []

    while not pause_detected and loop_count < loop_limit:
        nonsilent_chunks = detect_silence(
            audio,
            min_silence_len=min_silence_len,
            silence_thresh=silence_thresh
        )
        if len(nonsilent_chunks) > 0:
            pause_detected = True
        loop_count += 1
        silence_thresh += 4 # Increase the silence threshold for each loop
        min_silence_len -= 75 # Decrease the minimum silence length for each loop

    if pause_detected:
        # Calculate the end of speech by adding pause_extension to the end of the first non-silent chunk
        end_of_speech = nonsilent_chunks[0][0]
        clipped_audio = audio[:end_of_speech]
        return clipped_audio
    else:
        # Log a warning and return the original audio if no pauses are detected
        logging.warning("Could not detect a pause in the audio. Returning the original audio.")
        return audio
    
############################################
# Add a pause to the audio
############################################
def add_pause(audio, pause_duration=1000):
    pause = AudioSegment.silent(duration=pause_duration)
    return pause + audio