from dotenv import load_dotenv
import os
from datetime import datetime
import asyncio
from openai_helper import complete_openai
from speech_to_text_processing import Start_recording
from text_to_speech_processing import speak

# ---------------------------------------------------------------------------- #
#                                     Setup                                    #
# ---------------------------------------------------------------------------- #

load_dotenv(override=True)

settings = {
    'speechKey': os.environ.get('SPEECH_KEY'),
    'region': os.environ.get('SPEECH_REGION'),
    # Feel free to hardcode the language
    'language': os.environ.get('SPEECH_LANGUAGE'),
    'openAIKey': os.environ.get('OPENAI_KEY')
}

output_folder = f'./Output/{datetime.now().strftime("%Y%m%d_%H%M%S")}/'
os.makedirs(output_folder)
conversation = []

async def main():
    while True:
        res = (await Start_recording(output_folder=output_folder))[0]['text']
        conversation.append(res)
        transcript = datetime.now()
        print(f"[{transcript}] Transcript was appended to the conversation, next is making the openai call")
        
        prompt = ""
        for i in range(len(conversation) - 4, len(conversation)):
            if i >= 0:
                if i % 2 == 0:
                    prompt += f"Q: {conversation[i]}\n"
                else:
                    prompt += f"A: {conversation[i]}\n"
        prompt += "A: "
        print(prompt)
        
        result = complete_openai(prompt, token=200)
        conversation.append(result)
        appended_answer = datetime.now()
        print(f"[{appended_answer}] The generated answer was appended to the conversation, next is calling the speak function")
        
        speak(result, output_folder=output_folder)  # Synchronous call now

if __name__ == "__main__":
    asyncio.run(main())

