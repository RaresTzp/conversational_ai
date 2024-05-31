from dotenv import load_dotenv
import os
from datetime import datetime
import asyncio
import logging
from speech_to_text_processing import Start_recording
from text_to_speech_processing import speak_async
from openai_call import create_langchain_agent, query_langchain_agent
from langchain_core.messages import AIMessage  



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
# Initialize LangChain agent
agent_executor = create_langchain_agent()

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

        # Use the latest transcript as the prompt
        prompt = res[0]['text']
        logging.info(f"Generated prompt for LangChain: {prompt}")

        logging.info("Starting LangChain completion")
        langchain_start_time = datetime.now()
        result = await query_langchain_agent(agent_executor, prompt)
        langchain_end_time = datetime.now()
        logging.info(f"LangChain completion finished. Duration: {langchain_end_time - langchain_start_time}")

        if result:
            all_messages_content = []

            # Iterate over the result to extract AIMessage content
            for item in result:
                if 'agent' in item:
                    for message in item['agent']['messages']:
                        if isinstance(message, AIMessage) and message.content:
                            all_messages_content.append(message.content)
                        else:
                            logging.warning(f"Unexpected message type or empty content: {type(message)}")
                else:
                    logging.warning(f"Unexpected item type in result: {type(item)}")
                    print(f"Unexpected item type in result: {type(item)}")

            if all_messages_content:
                # Combine all AIMessage contents into a single response text
                response_text = " ".join(all_messages_content)
            else:
                response_text = "No response"

         
            
            conversation.append(response_text)
        else:
            logging.warning("No result received from LangChain")
            continue  # Skip to the next iteration if no result is received

        logging.info("Starting text-to-speech process")
        tts_start_time = datetime.now()
        await speak_async(response_text, output_folder=output_folder)
        tts_end_time = datetime.now()
        logging.info(f"TTS completed. Duration: {tts_end_time - tts_start_time}")



        turns += 1  # Increment the turn counter

    logging.info("Conversation completed")

if __name__ == "__main__":
    asyncio.run(main())
