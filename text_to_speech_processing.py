import azure.cognitiveservices.speech as speechsdk
from datetime import datetime
from sounds import play_sound
import simpleaudio as sa
from dotenv import load_dotenv
import os
import sounddevice as sd

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

def speak(text, silent=False, output_folder="./Output"):
    if text in already_spoken:  # if the speech was already synthesized
        if not silent:
            play_obj = sa.WaveObject.from_wave_file(already_spoken[text]).play()
            play_obj.wait_done()
        return

    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=settings['speechKey'], region=settings['region'])
    file_name = f'{output_folder}/{datetime.now().strftime("%Y%m%d_%H%M%S")}.wav'
    audio_config = speechsdk.audio.AudioOutputConfig(filename=file_name)

    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name = 'en-US-JennyNeural'

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    speech_synthesis_result = speech_synthesizer.speak_text(text)  # Synchronous call now
    synthesis_answer = datetime.now()
    print(f"[{synthesis_answer}] TTS pipeline started")
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Speech synthesized for text [{text}]")
        if not silent:
            received_answer = datetime.now()
            print(f"[{received_answer}] playing the speech")
            play_obj = sa.WaveObject.from_wave_file(file_name).play()
            play_obj.wait_done()
        already_spoken[text] = file_name
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")
            print("Did you set the speech resource key and region values?")

def speak_ssml(text):
    speech_config = speechsdk.SpeechConfig(subscription=settings['speechKey'], region=settings['region'])
    speech_config.speech_synthesis_voice_name = 'en-US-JennyNeural'
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    speech_synthesis_result = speech_synthesizer.speak_ssml(text)  # Synchronous call now

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Speech synthesized for text [{text}]")
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")
            print("Did you set the speech resource key and region values?")
