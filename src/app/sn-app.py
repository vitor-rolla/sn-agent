import streamlit as st
from openai import OpenAI
import yt_dlp
import os

# Page configuration
st.set_page_config(page_title="YouTube to GPT-4o Analyzer", page_icon="🎥")

# Load OpenAI API Key from st.secrets
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("Missing OpenAI API Key. Please configure it in .streamlit/secrets.toml")
    st.stop()

st.title("🎥 YouTube Audio Transcriber & Analyst")
st.markdown("Extract insights from YouTube videos using OpenAI's Whisper and GPT-4o.")

# Sidebar for configuration
with st.sidebar:
    st.header("Settings")
    prompt_template = st.text_area(
        "Analysis Prompt", 
        value="Please summarize the main points of the following transcription into bullet points:"
    )
    st.info("The audio is processed via Whisper API to optimize performance and memory usage.")

# User Input
video_url = st.text_input("Paste the YouTube video URL here:")

if video_url:
    try:
        # 1. Metadata Extraction (Thumbnail and Title)
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(video_url, download=False)
            title = info.get('title', 'No Title Found')
            thumbnail = info.get('thumbnail')

        st.subheader(f"📺 {title}")
        st.image(thumbnail, use_container_width=True)

        if st.button("Process Video"):
            with st.status("Processing...", expanded=True) as status:
                # 2. Audio Extraction
                st.write("Downloading audio...")
                audio_file_path = "temp_audio.m4a"
                
                ydl_opts = {
                    'format': 'm4a/bestaudio/best',
                    'outtmpl': 'temp_audio', # Extension added by postprocessor
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'm4a',
                    }],
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                
                # Check if file exists with correct extension
                if not os.path.exists(audio_file_path):
                    audio_file_path = "temp_audio.m4a"

                # 3. Transcription with Whisper
                st.write("Transcribing via Whisper API...")
                with open(audio_file_path, "rb") as audio_file:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1", 
                        file=audio_file
                    )
                
                # 4. Analysis with GPT-4o
                st.write("Analyzing with GPT-4o...")
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful research assistant."},
                        {"role": "user", "content": f"{prompt_template}\n\nTranscription:\n{transcript.text}"}
                    ]
                )
                
                status.update(label="Analysis Complete!", state="complete")

            # Display Results
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📝 Transcription")
                st.write(transcript.text)
            
            with col2:
                st.subheader("💡 GPT-4o Analysis")
                st.success(response.choices[0].message.content)

            # Cleanup
            if os.path.exists(audio_file_path):
                os.remove(audio_file_path)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")