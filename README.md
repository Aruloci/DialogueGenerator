# Dialogue Generator
This project was created as part of my bachelor thesis. It allows the user to create conversations including annotations. These conversations can be used to train speech models without having to manually record conversations and annotate data. The project offers a pipeline and a website to interact with the pipeline. The pipeline can also be run manually. 

![image](https://github.com/pfistdo/DialogueGenerator/assets/100299364/14127771-b5c6-4058-90d0-aea06a90f5a1)


# Getting started :rocket:
## Prerequisites
1. [OpenAI API key](https://platform.openai.com/api-keys)
2. [ElevenLabs API key](https://elevenlabs.io/)

## Installation
```bash
git clone https://github.com/pfistdo/DialogueGenerator/
```
### (Optional):
To run only the pipeline without the website the following step is required:
- Create a .env file in the root of the project. Place the API keys in the .env file and use the template below.
```bash
OPENAI_API_KEY=
ELEVENLABS_API_KEY=
```


# Usage :hammer_and_wrench:
To use the project there are 2 options which will be presented below.
## Option 1: Run the website
- Start the [webserver](https://github.com/pfistdo/DialogueGenerator/blob/main/start_webserver.py).
- Create an account and provide the [API keys](http://127.0.0.1:5000/keys).
- Select voices on [ElevenLabs](https://elevenlabs.io/app/voice-library) and save them in [VoiceLab](https://elevenlabs.io/app/voice-lab).
- [Create a training set](http://127.0.0.1:5000/create) by providing a dialoge description. Copy the VoiceIDs of the selected voices into the input field.
- You can now create and download the dialogue :)

## Option 2: Run the pipeline
- Make sure the API keys are saved in the .env file.
- In [main.py](https://github.com/pfistdo/DialogueGenerator/blob/main/main.py) adjust the conversation description. Search for `Add your conversation generation here`.
- Run the script.
- Output will be saved in `web\static\output\pipe_user`.


# API Description :clipboard:
This is only relevant if the website is being used. The pipeline does not use any API calls apart from OpenAI and ElevenLabs. 
To view a description of all created endpoints head over to Postman.
<br />:warning: Please note the webserver must be running to execute API calls.<br />
[![Run in Postman](https://run.pstmn.io/button.svg)]([https://app.getpostman.com/run-collection/ec29167cc815f290833e](https://documenter.getpostman.com/view/21116095/2sA3QqgYZa))


# Project structure :file_folder:
```Bash
DialogueGenerator/
┣ convtools/                     # Required to create annotations and merge audio files
┃ ┣ ambient_noise/               # Folder containing all ambient noise
┃ ┃ ┗ ...
┃ ┣ ir/					
┃ ┃ ┗  ...                       # Folder containing all impulse responses
┃ ┣ audioWriter.py			
┃ ┣ conversationFileReader.py
┃ ┣ rttmWriter.py
┃ ┗ textGridWriter.py
┣ instance/                      # SQLite DB to store user credentials
┃ ┗ db.sqlite
┣ web/                           # Webserver folder
┃ ┣ models/                      # Models. Only contains user related classes
┃ ┃ ┗ ...
┃ ┣ routes/                      # Flask routes
┃ ┃ ┗ ...
┃ ┣ static/                      # Flask static folder
┃ ┃ ┗ ...                
┃ ┣ templates/                   # Jinja templates folder containing all web pages
┃ ┃ ┣ components/                # Components that can be included
┃ ┃ ┃ ┗ ...              
┃ ┃ ┗ ...
┃ ┣ config.py                    # SQLite DB related configurations
┃ ┗ __init__.py                  # Create Flask app
┣ .env                           # Contains API keys to run pipeline
┣ .gitignore
┣ audio_utils.py                 # Functions to create audio data
┣ conversation_utils.py          # Functions to create conversation data
┣ main.py                        # Run the pipeline without website
┣ Procfile                       # Required for deployment on Heroku
┣ README.md
┣ requirements.txt
┣ runtime.txt                    # Required for deployment on Heroku
┗ start_webserver.py             # Start the webserver
```

# Contact
For any inquiries, please reach out to Dominic (dominic.pfister@swissonline.ch).
