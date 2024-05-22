import azure.cognitiveservices.speech as speechsdk
import time
from datetime import datetime
import simpleaudio as sa
from dotenv import load_dotenv
import os

load_dotenv(override=True)

settings = {
    'speechKey': os.environ.get('SPEECH_KEY'),
    'region': os.environ.get('SPEECH_REGION'),
    'language': os.environ.get('SPEECH_LANGUAGE'),
}

already_spoken = {}

def speak(text, silent=False, output_folder="./Output"):
    start_time = datetime.now()
    print(f"[{start_time}] TTS pipeline started")

    if text in already_spoken:  # if the speech was already synthesized
        if not silent:
            play_obj = sa.WaveObject.from_wave_file(already_spoken[text]).play()
            play_obj.wait_done()
        end_time = datetime.now()
        print(f"[{end_time}] TTS pipeline ended (cached speech)")
        return

    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=settings['speechKey'], region=settings['region'])
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    
    synth_start_time = datetime.now()
    print(f"[{synth_start_time}] Speech synthesis started")
    result = synthesizer.speak_text_async(text).get()
    synth_end_time = datetime.now()
    print(f"[{synth_end_time}] Speech synthesis ended")

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        output_path = os.path.join(output_folder, f"{text[:50]}.wav")
        with open(output_path, 'wb') as audio_file:
            audio_file.write(result.audio_data)
        already_spoken[text] = output_path
        if not silent:
            play_obj = sa.WaveObject.from_wave_file(output_path).play()
            play_obj.wait_done()
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")

    end_time = datetime.now()
    print(f"[{end_time}] TTS pipeline ended")

# Example usage
if __name__ == "__main__":
    speak("Hello, this is a test.")
