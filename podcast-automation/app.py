import streamlit as st
import streamlit.components.v1 as components
import os
import json
import shutil
import re
import textwrap
import requests
from elevenlabs.client import ElevenLabs
from elevenlabs import save, stream
from httpx import Timeout
from google.cloud import texttospeech
from pydub import AudioSegment
from vertexai.generative_models import GenerativeModel, GenerationConfig
import vertexai
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
os.environ["PATH"] += os.pathsep + os.path.expanduser("~/bin")
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
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Google TTS Client
client = texttospeech.TextToSpeechClient()
speaker_voice_map = {
    "Caesar": "BD7hFRsDGBBZDZZhNQ9M",
    "Grandpa Oxley": "NOpBlnGInO9m6vDvFkFC",
    "Archer (British)": "L0Dsvb3SLTyegXwtm47J",
    "Stuart (Australian)": "HDA9tsk27wYi3uq0fPcK",
}
voice_options = list(speaker_voice_map.keys())

# Retrieve ElevenLabs API key from environment
timeout_config = Timeout(180.0) 
elevenlabs_client = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY"),
)

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
    """
    Synthesizes speech using ElevenLabs API.
    """
    # Set the voice ID based on the speaker
    voice_id = "NOpBlnGInO9m6vDvFkFC"  # Default voice ID for ElevenLabs
    audio = elevenlabs_client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    filename = f"audio-files/{index}_{speaker}.mp3"
    with open(filename, "wb") as out:
        for chunk in audio:
            if chunk:
                out.write(chunk)
                
                
def split_text(text, max_length=2500):
    """
    Splits the input text into chunks of `max_length` characters
    without breaking sentences.
    """
    return textwrap.wrap(text, max_length, break_long_words=False, break_on_hyphens=False)       
def read_text_aloud_caesar(text, filename="output.mp3", chunks=False, audio_folder="audio-files", cleanup=True, voice_name="Caesar"): #TODO: handle larger articles and prevent timeouts from happening
    """
    Reads any text (e.g. article or story) aloud using the ElevenLabs "Caesar" voice.
    """
    #voice_id = "NOpBlnGInO9m6vDvFkFC" 
    if chunks: #can delete this first part because can use convert_as_stream
        os.makedirs(audio_folder, exist_ok=True)
        text_chunks = split_text(text, max_length=2500)
        for i, chunk in enumerate(text_chunks):
            audio = elevenlabs_client.text_to_speech.convert_as_stream(
                text=chunk,
                voice_id=speaker_voice_map.get(voice_name, "NOpBlnGInO9m6vDvFkFC"), #default to oxley
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )
            chunk_filename = os.path.join(audio_folder, f"output_chunk_{i + 1}.mp3")
            save(audio, chunk_filename)
            print(f"✅ Saved chunk {i + 1} to {chunk_filename}")

        # Merge all chunks after generation
        merge_audios(audio_folder, filename)
        if cleanup:
            shutil.rmtree(audio_folder)
    else:
        audio = elevenlabs_client.text_to_speech.convert_as_stream(
                text=text,
                voice_id=speaker_voice_map.get(voice_name, "NOpBlnGInO9m6vDvFkFC"),
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
        )
        with open(filename, "wb") as out: 
            for chunk in audio:
                if isinstance(chunk, bytes):
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
        with open(audio_path, "rb") as f:
            audio = AudioSegment.from_mp3(f)
        combined += audio
    combined.export(output_file, format="mp3")



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
col1, col2, col3, col4 = st.columns(4)

# Button definitions in separate columns
with col1:
    with st.form("generate_podcast_form"):
        generate_podcast_btn = st.form_submit_button("🔄 Generate A Podcast")

with col2:
    with st.form("read_article_form"):
        read_article_btn = st.form_submit_button("▶️ Read Me the Article 🎁")
        selected_voice = st.selectbox("Voice:", voice_options)

with col3:
    with st.form("story_form"):

        
        read_story_btn = st.form_submit_button("📚 Read Me A Story 🎄")
        selected_voice = st.selectbox("Voice:", voice_options)


    
with col4:
    with st.form("practice_dutch_form"):
        practice_dutch_btn = st.form_submit_button("Practice your Dutch 🇳🇱")
        if practice_dutch_btn:
            st.info("🇳🇱 Talk to Caesar and practice your Dutch!")
            components.html(
                """
                    
                <elevenlabs-convai agent-id="LxLNrURhKwzioyBbRZEx"></elevenlabs-convai>
                <script src="https://elevenlabs.io/convai-widget/index.js" async type="text/javascript"></script>
                """,
                height=200,
                width=383,
            )

# 1) Generate Podcast (TODO: only one not working at the moment!)
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
        st.info(f"🔊 Generating audio for the article with {selected_voice}'s voice...")
        # chunk_threshold = 2500  
        # use_chunks = len(article) > chunk_threshold
        article_audio = read_text_aloud_caesar(article, "article.mp3", voice_name=selected_voice)
        print(article_audio)
        st.audio(article_audio, format="audio/mp3")
        st.download_button(
            "🎁 Download Article Audio 🎁",
            data=open(article_audio, "rb"),
            file_name="article.mp3",
            mime="audio/mp3"
        )



def generate_story_with_openai(story_prompt):
    # Set your OpenAI API key

    # Call the OpenAI ChatCompletion API
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": story_prompt}
        ],
        max_tokens=4000,
        temperature=0.7,
        top_p=0.95,
        n=1,
        stop=None
    )

    # Extract the generated story text
    story_text = response.choices[0].message.content.strip()
    return story_text



# 3) Read Me Story
if read_story_btn:

    story_prompt = """
        Please generate an audio story. The narrator that will read out the story's name is Caesar. 
        The story should be a small rural village in England. Make it a goodnight story but for an older adult (25 years old). You may sprinkle a bit of magic in your story. 
        """

    # Dropdown for voice options
 
    
    st.info(f"🔊 Generating audio for the story with {selected_voice}'s voice...")
    story_text = generate_story_with_openai(story_prompt)
    st.text_area("Generated Story", story_text, height=300)
    story_audio = read_text_aloud_caesar(story_text, "story.mp3", voice_name=selected_voice)  # Assuming read_text_aloud_caesar can handle different voices
    st.audio(story_audio, format="audio/mp3")
    st.download_button(
        "🎁 Download Story Audio 🎁",
        data=open(story_audio, "rb"),
        file_name="story.mp3",
        mime="audio/mp3"
    )
    
# 4) new button for K to practice her Dutch (conversational agent)



### old code
# def generate_story_with_vertex_ai(story_prompt):
#     model = GenerativeModel("gemini-2.5-pro-exp-03-25", system_instruction=[story_prompt])
    
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


    # predefined_story = (
    #     "Once upon a time in a snowy village, there lived a kind little girl named Kirsty. "
    #     "She loved giving presents to children and spreading joy during the holiday season. "
    #     "One magical Christmas Eve, he decided to deliver gifts to every child in the village. "
    #     "With the help of his trusty reindeer, Nicholas flew across the sky, filling hearts "
    #     "with wonder and happiness. From that day on, he became known as Santa Claus, a "
    #     "symbol of love and generosity."
    # )
    
    # Vertex AI configuration to generate the conversation
generation_config = GenerationConfig(
    max_output_tokens=8192,
    temperature=1,
    top_p=0.95,
    response_mime_type="application/json",
    response_schema={"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"speaker": {"type": "STRING"}, "text": {"type": "STRING"}}}},
)