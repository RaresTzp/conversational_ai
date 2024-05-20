#Load the .env file
from dotenv import load_dotenv
#separate the env variables from the os
import os
from datetime import datetime
from speech_processing import start_recording

#load the env variables
load_dotenv(override=True)

settings = {
    'speechKey': os.environ.get('SPEECH_KEY'),
    'region': os.environ.get('SPEECH_REGION'),
    'language': os.environ.get('SPEECH_LANGUAGE'),
    'openAIKey': os.environ.get('OPENAI_KEY')
}
output_folder = f'./Output/{datetime.now().strftime("%Y%m%d_%H%M%S")}/'

output_folder = f'./Output/{datetime.now().strftime("%Y%m%d_%H%M%S")}/'
os.makedirs(output_folder)


speech = start_recording(output_folder=output_folder)[0]['DisplayText']