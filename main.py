from dotenv import load_dotenv
import os
from datetime import datetime
import asyncio
import logging
from openai_helper import complete_openai
from speech_to_text_processing import Start_recording
from text_to_speech_processing import speak_async

# ---------------------------------------------------------------------------- #
#                                     Setup                                    #
# ---------------------------------------------------------------------------- #

load_dotenv(override=True)

settings = {
    'speechKey': os.environ.get('SPEECH_KEY'),
    'region': os.environ.get('SPEECH_REGION'),
    'language': os.environ.get('SPEECH_LANGUAGE'),
    'openAIKey': os.environ.get('OPENAI_KEY')
}

output_folder = f'./Output/{datetime.now().strftime("%Y%m%d_%H%M%S")}/'
os.makedirs(output_folder)
conversation = []
max_turns = 4  # Maximum number of conversation turns

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    turns = 0
    while turns < max_turns:
        logging.info("Starting speech-to-text process")
        start_time = datetime.now()
        res = await Start_recording(output_folder=output_folder)
        stt_end_time = datetime.now()
        logging.info(f"STT completed. Duration: {stt_end_time - start_time}")

        if res:
            conversation.append(res[0]['text'])
            logging.info(f"Transcript appended at {stt_end_time}: {res[0]['text']}")
        else:
            logging.warning("No transcript received from STT process")
            continue  # Skip to the next iteration if no transcript is received

        prompt = ""
        for i in range(len(conversation) - 4, len(conversation)):
            if i >= 0:
                if i % 2 == 0:
                    prompt += f"Q: {conversation[i]}\n"
                else:
                    prompt += f"A: {conversation[i]}\n"
        prompt += "A: "
        logging.info(f"Generated prompt for OpenAI: {prompt}")

        logging.info("Starting OpenAI completion")
        openai_start_time = datetime.now()
        result = complete_openai(prompt, token=200)
        openai_end_time = datetime.now()
        logging.info(f"OpenAI completion finished. Duration: {openai_end_time - openai_start_time}")

        if result:
            conversation.append(result)
            logging.info(f"Generated answer appended at {openai_end_time}: {result}")
        else:
            logging.warning("No result received from OpenAI")
            continue  # Skip to the next iteration if no result is received

        logging.info("Starting text-to-speech process")
        tts_start_time = datetime.now()
        await speak_async(result, output_folder=output_folder)
        tts_end_time = datetime.now()
        logging.info(f"TTS completed. Duration: {tts_end_time - tts_start_time}")

        turns += 1  # Increment the turn counter

    logging.info("Conversation completed")

if __name__ == "__main__":
    asyncio.run(main())
