import azure.cognitiveservices.speech as speechsdk
from datetime import datetime
from sounds import play_sound
from dotenv import load_dotenv
import os
import sounddevice as sd
import asyncio

# List the available audio devices and their IDs
devices = sd.query_devices()
for i, device in enumerate(devices):
    print(f"Device {i}: {device['name']} (ID: {device['index']})")

load_dotenv(override=True)

settings = {
    'speechKey': os.environ.get('SPEECH_KEY'),
    'region': os.environ.get('SPEECH_REGION'),
    'language': os.environ.get('SPEECH_LANGUAGE'),
    'openAIKey': os.environ.get('OPENAI_KEY')
}

async def Start_recording(output_folder):
    # Creates an instance of a speech config with specified subscription key and service region.
    speech_config = speechsdk.SpeechConfig(subscription=settings['speechKey'], region=settings['region'])
    speech_config.request_word_level_timestamps()
    speech_config.set_property(property_id=speechsdk.PropertyId.SpeechServiceResponse_OutputFormatOption, value="detailed")

    # Creates a speech recognizer using the default microphone (built-in).
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    # Initialize some variables
    results = []
    done = False

    # Update the last time speech was detected.
    def speech_detected():
        nonlocal lastSpoken
        lastSpoken = int(datetime.now().timestamp() * 1000)

    # Event handler to add event to the result list
    def handleResult(evt):
        nonlocal results
        res = {'text': evt.result.text, 'timestamp': evt.result.offset, 'duration': evt.result.duration, 'raw': evt.result}
        speech_detected()
        text = res['text']
        print(f"text: {text}")
        if res['text']:
            results.append(res)

    # Event handler to check if the recognizer is done
    def stop_cb(evt):
        nonlocal done
        done = True
        stopping_recording = datetime.now()
        print(f"[{stopping_recording}] Stopping recording. Preparing to process the transcripts")

    speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.recognizing.connect(lambda evt: speech_detected())
    speech_recognizer.canceled.connect(stop_cb)
    speech_recognizer.recognized.connect(handleResult)

    # Start speech recognition
    result_future = speech_recognizer.start_continuous_recognition_async()
    result_future.get()

    # Play sound to indicate that the recording session is on.
    play_sound()

    lastSpoken = int(datetime.now().timestamp() * 1000)

    # Wait for speech recognition to complete
    while not done:
        await asyncio.sleep(1)
        now = int(datetime.now().timestamp() * 1000)
        inactivity = now - lastSpoken
        if inactivity > 1000:
            play_sound()
        if inactivity > 3000:
            print('Stopping async recognition.')
            stop_future = speech_recognizer.stop_continuous_recognition_async()
            stop_future.get()  # Wait for the stop recognition to complete
            break

    await asyncio.sleep(1)
    print(results)
    return results

