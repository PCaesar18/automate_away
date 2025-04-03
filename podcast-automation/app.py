import streamlit as st
import os
import json
import shutil
import re
import requests
import ElevenLabs
from google.cloud import texttospeech
from pydub import AudioSegment
from vertexai.generative_models import GenerativeModel, GenerationConfig
import vertexai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Streamlit configuration
# Streamlit configuration
st.set_page_config(page_title="You are my Roman Empire", layout="wide")
st.markdown(
    """
    <style>
        body {
            background-color: #228B22; /* Green background */
            color: #FF0000; /* Red text */
            font-family: 'Arial', sans-serif;
        }
        h1 {
            font-family: 'Merry Christmas', sans-serif;
            color: #FF4500; /* Orange-red for headers */
        }
        button {
            background-color: #FF0000;
            color: #FFFFFF;
        }
        button:hover {
            background-color: #B22222; /* Dark red on hover */
        }
        textarea {
            border: 2px solid #FF4500;
            background-color: #FFF8DC;
            color: #FF0000;
        }
        /* Snowflake animation */
        .snowflake {
            color: white;
            font-size: 1.2em;
            font-family: Arial, sans-serif;
            position: fixed;
            top: -10%;
            z-index: 9999;
            user-select: none;
            animation-name: snowflakes-fall, snowflakes-shake;
            animation-duration: 10s, 3s;
            animation-timing-function: linear, ease-in-out;
            animation-iteration-count: infinite, infinite;
        }
        @keyframes snowflakes-fall {
            0% { top: -10%; }
            100% { top: 100%; }
        }
        @keyframes snowflakes-shake {
            0% { transform: translateX(0); }
            50% { transform: translateX(80px); }
            100% { transform: translateX(0); }
        }
    </style>
    <div class="snowflake" style="left: 10%;">❄️</div>
    <div class="snowflake" style="left: 20%;">❄️</div>
    <div class="snowflake" style="left: 30%;">❄️</div>
    <div class="snowflake" style="left: 40%;">❄️</div>
    <div class="snowflake" style="left: 50%;">❄️</div>
    <div class="snowflake" style="left: 60%;">❄️</div>
    <div class="snowflake" style="left: 70%;">❄️</div>
    <div class="snowflake" style="left: 80%;">❄️</div>
    <div class="snowflake" style="left: 90%;">❄️</div>
    """,
    unsafe_allow_html=True,
)

st.title("🎙️ Kirsty's Caesar in a Box 👑🎁 ")

# System prompt for Vertex AI
system_prompt = """you are an experienced podcast host...
- based on text like an article you can create an engaging conversation between two people.
- make the conversation at least 30000 characters long with a lot of emotion.
- in the response for me to identify use Caesar and David.
- Caesar is writing the articles and David is the second speaker that is asking all the good questions.
- The podcast is called The Machine Learning Engineer.
- Short sentences that can be easily used with speech synthesis.
- excitement during the conversation.
- do not mention last names.
- Caesar and David are doing this podcast together. Avoid sentences like: "Thanks for having me, David!"
- Include filler words like äh to make the conversation more natural.
"""
vertexai.init(project="upbeat-bolt-272721", location="australia-southeast1")

# Google TTS Client
client = texttospeech.TextToSpeechClient()
speaker_voice_map = {
    "Caesar": "ElevenLabs",
    "David": "en-US-Journey-O"
}

# Retrieve ElevenLabs API key from environment
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
elevenlabs_url = "https://api.elevenlabs.io/v1/text-to-speech/ERL3svWBAQ18ByCZTr4k"
elevenlabs_headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": elevenlabs_api_key
}

# Google TTS function
def synthesize_speech_google(text, speaker, index):
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=speaker_voice_map[speaker]
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    filename = f"audio-files/{index}_{speaker}.mp3"
    with open(filename, "wb") as out:
        out.write(response.audio_content)

# ElevenLabs TTS function
def synthesize_speech_elevenlabs(text, speaker, index):
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(elevenlabs_url, json=data, headers=elevenlabs_headers)
    filename = f"audio-files/{index}_{speaker}.mp3"
    with open(filename, "wb") as out:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                out.write(chunk)
                
                
                
def read_text_aloud_caesar(text, filename="output.mp3"):
    """
    Reads any text (e.g. article or story) aloud using the ElevenLabs "Caesar" voice.
    """
    data = {
        "text": text,
        "voice_id": "NOpBlnGInO9m6vDvFkFC",
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(elevenlabs_url, json=data, headers=elevenlabs_headers)
    with open(filename, "wb") as out: 
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                out.write(chunk)
    return filename

# Function to synthesize speech based on the speaker
def synthesize_speech(text, speaker, index):
    if speaker == "Caesar":
        synthesize_speech_elevenlabs(text, speaker, index)
    else:
        synthesize_speech_google(text, speaker, index)

# Function to sort filenames naturally
def natural_sort_key(filename):
    return [int(text) if text.isdigit() else text for text in re.split(r'(\d+)', filename)]

# Function to merge audio files
def merge_audios(audio_folder, output_file):
    combined = AudioSegment.empty()
    audio_files = sorted(
        [f for f in os.listdir(audio_folder) if f.endswith(".mp3") or f.endswith(".wav")],
        key=natural_sort_key
    )
    for filename in audio_files:
        audio_path = os.path.join(audio_folder, filename)
        audio = AudioSegment.from_file(audio_path)
        combined += audio
    combined.export(output_file, format="mp3")

# Vertex AI configuration to generate the conversation
generation_config = GenerationConfig(
    max_output_tokens=8192,
    temperature=1,
    top_p=0.95,
    response_mime_type="application/json",
    response_schema={"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"speaker": {"type": "STRING"}, "text": {"type": "STRING"}}}},
)

# Function to calculate costs based on token counts
def calculate_cost(prompt_token_count, candidates_token_count):
    cost_per_1k_chars = 0.0000046875
    total_chars = prompt_token_count + candidates_token_count
    total_cost = (total_chars / 1000) * cost_per_1k_chars
    return total_cost

# Function to generate the conversation using Vertex AI
def generate_conversation(article):
    model = GenerativeModel("gemini-1.5-flash-002", system_instruction=[system_prompt])
    responses = model.generate_content([article], generation_config=generation_config, stream=False)
    
    json_response = responses.candidates[0].content.parts[0].text
    json_data = json.loads(json_response)
    return json_data

# Function to generate the podcast audio from conversation data
def generate_audio(conversation):
    if os.path.exists('audio-files'):
        shutil.rmtree('audio-files')
    os.makedirs('audio-files', exist_ok=True)
    
    for index, part in enumerate(conversation):
        speaker = part['speaker']
        text = part['text']
        synthesize_speech(text, speaker, index)
    
    output_file = "podcast.mp3"
    merge_audios("audio-files", output_file)
    return output_file

# Streamlit inputs and outputs
article = st.text_area("🎁 Article Content 🎁", "Paste the article text here", height=300)
# Use columns to place buttons side by side
col1, col2, col3 = st.columns(3)

# Button definitions in separate columns
with col1:
    generate_podcast_btn = st.button(" 🔄 Generate A Podcast ")

with col2:
    read_article_btn = st.button("▶️ Read Me the Article 🎁")

with col3:
    read_story_btn = st.button("📚Read Me A Story 🎄")

# 1) Generate Podcast
if generate_podcast_btn:
    if not article:
        st.error("⛔ Please enter article content to generate a podcast. 🎁")
    else:
        with st.spinner("🎶 Generating conversation... 🎶"):
            conversation = generate_conversation(article)
        
        st.success("✅ Conversation generated successfully! 🎉")
        st.json(conversation)
        
        # Generate audio files
        with st.spinner("🔔 Synthesizing audio... 🔔"):
            podcast_file = generate_audio(conversation)
        
        st.success("🎧 Audio ready to play! 🎶")
        st.audio(podcast_file, format="audio/mp3")
        st.download_button(
            "🎁 Download Podcast 🎁",
            data=open(podcast_file, "rb"),
            file_name="podcast.mp3",
            mime="audio/mp3"
        )

# 2) Read Me the Article
if read_article_btn:
    if not article:
        st.error("⛔ Please enter article content to read it aloud.")
    else:
        st.info("🔊 Generating audio for the article with Caesar's voice...")
        article_audio = read_text_aloud_caesar(article, "article.mp3")
        print(article_audio)
        st.audio(article_audio, format="audio/mp3")
        st.download_button(
            "🎁 Download Article Audio 🎁",
            data=open(article_audio, "rb"),
            file_name="article.mp3",
            mime="audio/mp3"
        )

def generate_story_with_vertex_ai(story_prompt):
    model = GenerativeModel("gemini-2.5-pro-exp-03-25", system_instruction=[story_prompt])
    
    # Adjust the generation configuration as needed
    story_generation_config = GenerationConfig(
        max_output_tokens=65536,
        temperature=0.7,
        top_p=0.95,
        response_mime_type="application/json",
        response_schema={"type": "STRING"}
    )
    
    responses = model.generate_content([story_prompt], generation_config=story_generation_config, stream=False)
    

    story_text = responses.candidates[0].content.parts[0].text
    return story_text

# 3) Read Me Story
if read_story_btn:
    # predefined_story = (
    #     "Once upon a time in a snowy village, there lived a kind little girl named Kirsty. "
    #     "She loved giving presents to children and spreading joy during the holiday season. "
    #     "One magical Christmas Eve, he decided to deliver gifts to every child in the village. "
    #     "With the help of his trusty reindeer, Nicholas flew across the sky, filling hearts "
    #     "with wonder and happiness. From that day on, he became known as Santa Claus, a "
    #     "symbol of love and generosity."
    # )
    story_prompt = """
        Please generate an audio story. The narrator that will read out the story's name is Caesar. 
        The story should be a small rural village in England. Make it a goodnight story but for an older adult (25 years old). You may sprinkle a bit of magic in your story. 
        """

    
    st.info("🔊 Generating audio for the story with Caesar's voice...")
    story_text = generate_story_with_vertex_ai(story_prompt)
    st.text_area("Generated Story", story_text, height=300)
    story_audio = read_text_aloud_caesar(story_text, "story.mp3")
    st.audio(story_audio, format="audio/mp3")
    st.download_button(
        "🎁 Download Story Audio 🎁",
        data=open(story_audio, "rb"),
        file_name="story.mp3",
        mime="audio/mp3"
    )
