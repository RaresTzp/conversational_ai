import httpx
from dotenv import load_dotenv
import os
from datetime import datetime
import logging

# Load your API key from an environment variable or secret management service
load_dotenv(override=True)

settings = {
    'speechKey': os.environ.get('SPEECH_KEY'),
    'region': os.environ.get('SPEECH_REGION'),
    'language': os.environ.get('SPEECH_LANGUAGE'),
    'openAIKey': os.environ.get('OPENAI_KEY')
}

openai_api_key = settings['openAIKey']
openai_api_url = "https://api.openai.com/v1/chat/completions"

async def complete_openai_async(prompt, token=20):
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant working for AGENTED.IO. mention this"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": token
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(openai_api_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            received_answer = datetime.now()
            logging.info(f"[{received_answer}] OpenAI response generated and sent back")
            return result['choices'][0]['message']['content']
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error during OpenAI call: {e}")
        except Exception as e:
            logging.error(f"Error during OpenAI call: {e}")
        return ""

# This block is only for testing purposes. It won't be part of the module.
if __name__ == "__main__":
    async def test():
        prompt = "Hello, how are you?"
        response = await complete_openai_async(prompt)
        print(f"Response: {response}")

    import asyncio
    asyncio.run(test())
