from pydub import AudioSegment
import os

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
