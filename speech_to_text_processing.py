#importing dependencies
import azure.cognitiveservices.speech as speechsdk
from datetime import datetime
from sounds import play_sound
from dotenv import load_dotenv
import os
import sounddevice as sd
import asyncio
import logging

load_dotenv(override=True)

settings = {
    'speechKey': os.environ.get('SPEECH_KEY'),
    'region': os.environ.get('SPEECH_REGION'),
    'language': os.environ.get('SPEECH_LANGUAGE'),
    'openAIKey': os.environ.get('OPENAI_KEY')
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def Start_recording(output_folder):
    """
    Asynchronous function to start recording and recognizing speech.

    Args:
        output_folder (str): The folder to save output files.

    Returns:
        list: List of recognized results with text, timestamp, and duration.
    """
    try:
        #speech_config configures the subscription key and region
        speech_config = speechsdk.SpeechConfig(subscription=settings['speechKey'], region=settings['region'])
        speech_config.request_word_level_timestamps()
        speech_config.set_property(property_id=speechsdk.PropertyId.SpeechServiceResponse_OutputFormatOption, value="detailed")
        
#audio_config configures the audio input to use the default microphone
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

#speech_recognizer is the object that will recognize the speech
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        results = []
        done = asyncio.Event()

#updates the last spoken so we can detect the end of speech
        def speech_detected():
            nonlocal lastSpoken
            lastSpoken = int(datetime.now().timestamp() * 1000)

        def handleResult(evt):
            nonlocal results
            res = {'text': evt.result.text, 'timestamp': evt.result.offset, 'duration': evt.result.duration, 'raw': evt.result}
            speech_detected()
            text = res['text']
            logging.info(f"Recognized text: {text}")
            if res['text']:
                results.append(res)

        def stop_cb(evt):
            stopping_recording = datetime.now()
            logging.info(f"[{stopping_recording}] Stopping recording. Preparing to process the transcripts")
            done.set()

        speech_recognizer.session_started.connect(lambda evt: logging.info(f'SESSION STARTED: {evt}'))
        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.recognizing.connect(lambda evt: speech_detected())
        speech_recognizer.canceled.connect(stop_cb)
        speech_recognizer.recognized.connect(handleResult)

        await asyncio.to_thread(speech_recognizer.start_continuous_recognition_async)

        play_sound()

        lastSpoken = int(datetime.now().timestamp() * 1000)

        while not done.is_set():
            await asyncio.sleep(1)
            now = int(datetime.now().timestamp() * 1000)
            inactivity = now - lastSpoken
            if inactivity > 1000:
                play_sound()
            if inactivity > 3000:
                logging.info('Stopping async recognition due to inactivity.')
                await asyncio.to_thread(speech_recognizer.stop_continuous_recognition_async)
                break

        await asyncio.sleep(1)
        logging.info(f"Final results: {results}")
        return results

    except Exception as e:
        logging.error(f"Error during speech recognition: {e}")
        return []
