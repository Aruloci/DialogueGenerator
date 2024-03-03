import os
import requests

from pydub import AudioSegment


output_dir = 'output/' # Where the output files will be saved

############################################
# Text to speech using the Eleven Labs API
############################################
def generate_elevenlabs_audio(text_id: int, text: str, speaker: str, timing: int = 0, emotion: str = "neutral"):
    CHUNK_SIZE = 1024
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{speaker}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": os.environ.get("ELEVENLABS_API_KEY")
    }
    data = {
        "text": f'{text}<break time="2.0s" />he said {emotion}ly.',
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    print(data)
    response = requests.post(url, json=data, headers=headers)
    with open(f"{output_dir}output{text_id}.mp3", 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

############################################
# Merge multiple audio files into one
############################################
def merge_audio_files(input_files, output_file):
    # Initialize an empty audio segment
    merged_audio = AudioSegment.empty()

    # Iterate over each input file
    for file in input_files:
        # Load the audio file
        audio_segment = AudioSegment.from_file(file)

        # Add the audio segment to the merged audio
        merged_audio += audio_segment

    # Save the concatenated audio file
    merged_audio.export(output_file, format="mp3")