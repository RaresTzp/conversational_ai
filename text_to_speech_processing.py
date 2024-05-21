import azure.cognitiveservices.speech as speechsdk
import time
from datetime import datetime
# from main import settings, already_spoken, output_folder
from sounds import play_sound
import simpleaudio as sa
from dotenv import load_dotenv
import os
import sounddevice as sd

load_dotenv(override=True)

already_spoken = {}

settings = {
    'speechKey': os.environ.get('SPEECH_KEY'),
    'region': os.environ.get('SPEECH_REGION'),
    # Feel free to hardcode the language
    'language': os.environ.get('SPEECH_LANGUAGE'),
    'openAIKey': os.environ.get('OPENAI_KEY')
}

def speak(text, silent=False, output_folder="./Output"):

    if text in already_spoken:  # if the speech was already synthetized
        if not silent:
            play_obj = sa.WaveObject.from_wave_file(
                already_spoken[text]).play()
            play_obj.wait_done()
        return

    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(
        subscription=settings['speechKey'], region=settings['region'])
    # audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    file_name = f'{output_folder}/{datetime.now().strftime("%Y%m%d_%H%M%S")}.wav'
    audio_config = speechsdk.audio.AudioOutputConfig(
        use_default_speaker=True, filename=file_name)

    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name = 'en-US-JennyNeural'

    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config)

    speech_synthesis_result = speech_synthesizer.speak_text(text)  # .get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
        if not silent:
            play_obj = sa.WaveObject.from_wave_file(file_name).play()
            play_obj.wait_done()
        already_spoken[text] = file_name
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(
            cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(
                    cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")


def speak_ssml(text):
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(
        subscription=settings['speechKey'], region=settings['region'])
    # audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name = 'en-US-JennyNeural'

    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=None)

    speech_synthesis_result = speech_synthesizer.speak_ssml(
        text)  # .speak_text(text) #.get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(
            cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(
                    cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")