# Project setup
1. Create a new virtual environment with 'python -m venv venv'
2. Activate the venv using 'venv\Scripts\activate'
3. Install all required dependencies with 'pip install -r requirements.txt'
4. It's important to run 'ffdl install --add-path' after install all requirements.

1. Generate OpenAI API key at https://platform.openai.com/api-keys
2. Put the generated key in the .env file in the root of this project and use OPENAI_API_KEY as environment variable.
3. Generate ElevenLabs API key at https://elevenlabs.io/ at bottom left in your profile.
4. Put the generated key in the .env file in the root of this project and use ELEVENLABS_API_KEY as environment variable.