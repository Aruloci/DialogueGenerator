import os
import requests
from io import BytesIO

from pydub import AudioSegment
from pydub.silence import detect_nonsilent


output_dir = 'output/' # Where the output files will be saved

############################################
# Text to speech using the Eleven Labs API
############################################
def generate_elevenlabs_audio(text_id: int, text: str, speaker: str, timing: int, emotion: str = "neutral"):
    CHUNK_SIZE = 1024
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{speaker}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": os.environ.get("ELEVENLABS_API_KEY")
    }
    data = {
        "text": f'{text}<break time="4.0s" />he said {emotion}ly.',
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    response = requests.post(url, json=data, headers=headers)

    audio_buffer = BytesIO()
    # Write each chunk of data to the BytesIO buffer
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
        if chunk:
            audio_buffer.write(chunk)
    audio_buffer.seek(0) # Reset the buffer position to the beginning
    audio_segment = AudioSegment.from_file(audio_buffer, format="mp3")

    audio_segment = clip_audio_at_pause(audio_segment, pause_extension=timing*1000) # Clip audio at pause to remove "he said" part
    return audio_segment

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
# Clip audio when a pause is detected
############################################
def clip_audio_at_pause(audio, min_silence_len=1000, silence_thresh=-50, pause_extension=500):

    # Detect non-silent chunks
    nonsilent_chunks = detect_nonsilent(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh
    )

    # If none are detected, return the original audio
    if not nonsilent_chunks:
        return audio

    end_of_speech = nonsilent_chunks[0][1] 
    clipped_audio = audio[:end_of_speech]

    return AudioSegment.silent(duration=pause_extension) + clipped_audio