import azure.cognitiveservices.speech as speechsdk
from datetime import datetime
from sounds import play_sound
import simpleaudio as sa
from dotenv import load_dotenv
import os
import sounddevice as sd
import asyncio
import logging

# List the available audio devices and their IDs
devices = sd.query_devices()
for i, device in enumerate(devices):
    print(f"Device {i}: {device['name']} (ID: {device['index']})")

load_dotenv(override=True)

already_spoken = {}

settings = {
    'speechKey': os.environ.get('SPEECH_KEY'),
    'region': os.environ.get('SPEECH_REGION'),
    'language': os.environ.get('SPEECH_LANGUAGE'),
    'openAIKey': os.environ.get('OPENAI_KEY')
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def speak_async(text, silent=False, output_folder="./Output"):
    """
    Asynchronous function to synthesize and play speech.

    Args:
        text (str): The text to be synthesized.
        silent (bool): If True, do not play the synthesized speech.
        output_folder (str): The folder to save output files.

    Returns:
        None
    """
    try:
        if text in already_spoken:  # if the speech was already synthesized
            if not silent:
                play_obj = sa.WaveObject.from_wave_file(already_spoken[text]).play()
                await asyncio.to_thread(play_obj.wait_done)
            return

        # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
        speech_config = speechsdk.SpeechConfig(subscription=settings['speechKey'], region=settings['region'])
        file_name = f'{output_folder}/{datetime.now().strftime("%Y%m%d_%H%M%S")}.wav'
        audio_config = speechsdk.audio.AudioOutputConfig(filename=file_name)

        # The language of the voice that speaks.
        speech_config.speech_synthesis_voice_name = 'en-US-JennyNeural'

        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        synthesis_answer = datetime.now()
        logging.info(f"[{synthesis_answer}] TTS pipeline started")

        # Use asyncio.to_thread to run the blocking speak_text method
        speech_synthesis_result = await asyncio.to_thread(speech_synthesizer.speak_text, text)
        
        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logging.info(f"Speech synthesized for text [{text}]")
            if not silent:
                received_answer = datetime.now()
                logging.info(f"[{received_answer}] playing the speech")
                play_obj = sa.WaveObject.from_wave_file(file_name).play()
                await asyncio.to_thread(play_obj.wait_done)
            already_spoken[text] = file_name
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            logging.error(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                logging.error(f"Error details: {cancellation_details.error_details}")
                logging.error("Did you set the speech resource key and region values?")
    except Exception as e:
        logging.error(f"Error during speech synthesis: {e}")

async def speak_ssml_async(text):
    """
    Asynchronous function to synthesize speech from SSML.

    Args:
        text (str): The SSML text to be synthesized.

    Returns:
        None
    """
    try:
        speech_config = speechsdk.SpeechConfig(subscription=settings['speechKey'], region=settings['region'])
        speech_config.speech_synthesis_voice_name = 'en-US-JennyNeural'
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

        # Use asyncio.to_thread to run the blocking speak_ssml method
        speech_synthesis_result = await asyncio.to_thread(speech_synthesizer.speak_ssml, text)

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logging.info(f"Speech synthesized for text [{text}]")
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            logging.error(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                logging.error(f"Error details: {cancellation_details.error_details}")
                logging.error("Did you set the speech resource key and region values?")
    except Exception as e:
        logging.error(f"Error during speech synthesis: {e}")

# This block is only for testing purposes. It won't be part of the module.
if __name__ == "__main__":
    async def test():
        await speak_async("Hello, this is a test of the asynchronous TTS system.", silent=False, output_folder="./Output")
        await speak_ssml_async("<speak>Hello, this is a test of the asynchronous SSML TTS system.</speak>")

    asyncio.run(test())
