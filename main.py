import logging

from conversation_utils import create_audio, send_openai_request

# Set up logging
logging.basicConfig(level=logging.INFO)  # Set the logging level

messages=[
    {
        "role": "system",
        "content": """You are an expert in generating conversations based on the users requirements. Your goal is to generate a natural conversation 
        based on the scenario set by the user. To make a conversation feel more natural you should annotate every sentence with fitting emotions. Speakers
        should also be able to interrupt or talk over each other. To generate the conversation stick to the following format: 
            - Name: Name of the speaker. If no names are given generate names.
            - Text: The generated sentence for the speaker. Use ... and - to indicate a pause or stutter. Use comic speech like "Uhm", "Hmph", "Argh" to create a more natural conversation.
            - Emotion: The corresponding emotion of the speakers sentence.
            - Timing: The time in seconds between the current and previous sentence as double. Use 0.0 if the sentence starts immediately after the last one. Use any positive like 0.5 or 1.0 as
            double to create a small pause. A negative double indicates that the sentences overlap each other. Make sure that the timing is consistent with the whole conversation and feels natural.
            - Voice: The elevent labs voice id to use for the sentence. Use "H1oKRJV3pAGTo5Un0uwG" for male speakers and "Mr0lS24b2pkDEz6noGEd" or "otVgZoZFXk2SZDc0eBdZ" for female speakers. If there are
            multiple female speakers choose one voice for each of them. The voice should be the same for the same speaker throughout the conversation. Make sure that no voice is used for multiple speakers.

        To make the generated conversation easier to parse create a JSON formatted output. The root of the JSON object is called "conversation". Make sure the keys are named "Name", "Text", "Emotion", "Timing" and "Voice".
        One conversation should contain at least 10 sentences but should contain more.
        Did you understand that?""",
    }, 
    {
        "role": "user",
        # "content": "Generate a dialog between two females which are talking to a male conductor about the delay of a train at the trainstation.",
        "content": "Generate a dialog between a boss and his employee about his bad performance at work.",
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
        Optimize the timing (pauses) and emotions of the conversation to make it sound more natural.
        The conversation should feel like a real dialogue between real people. Keep the JSON format and the structure of the conversation.
        """
})
conversation = send_openai_request(messages)

# Generate conversation and process audio files
create_audio(conversation)