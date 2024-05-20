from openai import OpenAI
import openai
from dotenv import load_dotenv
import os
# from main import settings

# Load your API key from an environment variable or secret management service


load_dotenv(override=True)

settings = {
    'speechKey': os.environ.get('SPEECH_KEY'),
    'region': os.environ.get('SPEECH_REGION'),
    # Feel free to hardcode the language
    'language': os.environ.get('SPEECH_LANGUAGE'),
    'openAIKey': os.environ.get('OPENAI_KEY')
}

client = OpenAI(api_key=settings['openAIKey'])

def complete_openai(prompt, token=20):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant working for AGENTED.IO. mention this"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=token
    )
    return response.choices[0].message.content


