from google.cloud import texttospeech
from dotenv import load_dotenv
from google.cloud import texttospeech_v1beta1 as texttospeech
import os
import streamlit as st
import os
import json
import shutil
import re
import yaml
import requests
from google.cloud import texttospeech
from pydub import AudioSegment
from vertexai.generative_models import GenerativeModel, GenerationConfig
import vertexai
from dotenv import load_dotenv
import openai
# Load environment variables from .env file
load_dotenv()

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from podcastfy.client import generate_podcast
API_KEYS = {
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY"),
}
load_dotenv()
os.environ["PATH"] += os.pathsep + os.path.expanduser("~/bin")
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY"),
)

prompt =   (
         "Please generate an audio story. The narrator that will read out the story's name is Caesar. "
        "The story should be a small rural village in England. Make it a goodnight story but for an older adult (25 years old). You may sprinkle a bit of magic in your story. "
       
    )

conversation_config = {
    "roles_person1": "History Ph.D.",
    "roles_person2": "Creative Professor",
    "podcast_name": "The History Podcast",
    "podcast_tagline": "Because History is Everywhere",
    "creativity": 1,
    "user_instructions": "Speakers should often overlap in their sentences. The conversation should be about the relationship between History and life. Person2 should make connections with her own life!"
}

def load_config(config_path="conversation_config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

conversation_config = load_config()
#python -m podcastfy.client --tts-model elevenlabs --conversation-config conversation_config.yaml --url https://en.wikipedia.org/wiki/History_of_the_United_Kingdom --api-key-label OPENAI_API_KEY
audio_file = generate_podcast(
    urls=["https://en.wikipedia.org/wiki/History_of_the_United_Kingdom"],
    tts_model='elevenlabs',
    #llm_model_name="gpt-4o",
    api_key_label="OPENAI_API_KEY",
    conversation_config=conversation_config)

# def generate_story_with_vertex_ai(story_prompt):
#     vertexai.init(project="upbeat-bolt-272721", location="australia-southeast1")
#     model = GenerativeModel("gemini-1.5-flash-002", system_instruction=[story_prompt])
    
#     # Adjust the generation configuration as needed
#     story_generation_config = GenerationConfig(
#         max_output_tokens=65536,
#         temperature=0.7,
#         top_p=0.95,
#         response_mime_type="application/json",
#         response_schema={"type": "STRING"}
#     )
    
#     responses = model.generate_content([story_prompt], generation_config=story_generation_config, stream=False)
    

#     story_text = responses.candidates[0].content.parts[0].text
#     return story_text



def generate_story_with_openai(story_prompt):
    # Set your OpenAI API key

    # Call the OpenAI ChatCompletion API
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": story_prompt}
        ],
        max_tokens=1500,
        temperature=0.7,
        top_p=0.95,
        n=1,
        stop=None
    )

    # Extract the generated story text
    story_text = response.choices[0].message.content.strip()
    return story_text


text= generate_story_with_openai(prompt)

#text = generate_story_with_vertex_ai(prompt) #vertex seems to not be working, check payments


# audio = client.text_to_speech.convert(
#     text=text,
#     voice_id="NOpBlnGInO9m6vDvFkFC",
#     model_id="eleven_multilingual_v2",
#     output_format="mp3_44100_128",
# )
def download(audio, filename="test.mp3"):
    with open(filename, "wb") as out_file:
        # Iterate over the generator to write the audio content
        for chunk in audio:
            out_file.write(chunk)
    print(f"Audio content written to file '{filename}'")

# # Usage

from IPython.display import Audio, display

def embed_audio(audio_file):
	"""
	Embeds an audio file in the notebook, making it playable.

	Args:
		audio_file (str): Path to the audio file.
	"""
	try:
		display(Audio(audio_file))
		print(f"Audio player embedded for: {audio_file}")
	except Exception as e:
		print(f"Error embedding audio: {str(e)}")
embed_audio(audio_file)

# #play(audio)


# def test_tts():
#     client = texttospeech.TextToSpeechClient()
#     multi_speaker_markup = texttospeech.MultiSpeakerMarkup(
#     turns=[
#         texttospeech.MultiSpeakerMarkup.Turn(
#             text="I've heard that Kirsty really likes listening to podcasts, which is just amazing!",
#             speaker="R",
#         ),
#         texttospeech.MultiSpeakerMarkup.Turn(
#             text="Oh? What's so good about it?", speaker="S"
#         ),
#         texttospeech.MultiSpeakerMarkup.Turn(text="Well..", speaker="R"),
#         texttospeech.MultiSpeakerMarkup.Turn(text="Well what?", speaker="S"),
#         texttospeech.MultiSpeakerMarkup.Turn(
#             text="Well, you should find it out by yourself!", speaker="R"
#         ),
#         texttospeech.MultiSpeakerMarkup.Turn(
#             text="Alright alright, let's try it out!", speaker="S"
#         ),
#     ]
# )

    
#     synthesis_input = texttospeech.SynthesisInput(multi_speaker_markup=multi_speaker_markup)
#     voice = texttospeech.VoiceSelectionParams(language_code="en-US", name="en-US-Studio-MultiSpeaker")
#     audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

#     response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

#     with open("output.mp3", "wb") as out:
#         out.write(response.audio_content)
#     print("Audio content written to file 'output.mp3'")

# test_tts()
