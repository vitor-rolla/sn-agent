import streamlit as st
from openai import OpenAI
import google.generativeai as genai
import yt_dlp
import os
import requests
import json
import re

# Page configuration
st.set_page_config(page_title="YouTube to GPT-4o Analyzer", page_icon="🎥")

# Load OpenAI API Key from st.secrets
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("Missing OpenAI API Key. Please configure it in .streamlit/secrets.toml")
    st.stop()

if "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    except Exception as e:
        st.warning(f"Could not configure Google Gemini: {str(e)}")

# Load prompts from files
def load_prompts():
    prompts_dir = os.path.join(os.path.dirname(__file__), "../../data/prompts")
    prompts = {}
    for prompt_file in ["default.txt", "literal.txt", "complex.txt"]:
        file_path = os.path.join(prompts_dir, prompt_file)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                prompt_name = prompt_file.replace(".txt", "").capitalize()
                prompts[prompt_name] = f.read().strip()
    return prompts

prompts = load_prompts()

st.title("🎥 YouTube Soccer Narratives Agent")
st.markdown("Extract insights from YouTube soccer videos by analyzing their subtitles.")

# Sidebar for configuration
with st.sidebar:
    # Display logo
    logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    
    st.header("Settings")
    
    # Model selection
    st.subheader("🤖 Select Model")
    model = st.selectbox(
        "Choose your AI model:",
        options=["gemini-3-flash-preview", "o3"],
        help="Select between Google's Gemini 3 Flash Preview or OpenAI's O3"
    )
    
    # Prompt selection
    st.subheader("📋 Select Prompt")
    selected_prompt_name = st.selectbox(
        "Choose your analysis prompt:",
        options=list(prompts.keys()),
        help="Select between different prompt templates"
    )
    prompt_template = prompts.get(selected_prompt_name, "Please analyze the following transcription:")
    
    st.info("Subtitles are extracted directly from the video metadata.")

# Function to extract subtitle text from subtitles dict
def extract_subtitle_text(subtitles_dict, automatic_captions_dict=None):
    """Extract text from subtitles dictionary (manual or automatic)"""
    
    def parse_subtitle_content(content):
        """Parse subtitle content in various formats"""
        lines = []
        
        # Try to parse as JSON (YouTube json3 format)
        try:
            data = json.loads(content)
            if 'events' in data:
                for event in data['events']:
                    if 'segs' in event:
                        text_parts = []
                        for seg in event['segs']:
                            if 'utf8' in seg:
                                text = seg['utf8'].strip()
                                # Skip newline markers
                                if text and text != '\n':
                                    text_parts.append(text)
                        if text_parts:
                            lines.append(' '.join(text_parts))
                return '\n'.join(lines)
        except:
            pass
        
        # Try to parse as SRT/VTT
        for line in content.split('\n'):
            line = line.strip()
            # Skip empty lines, numbers, timestamps, and XML tags
            if line and not line.isdigit() and '-->' not in line and not line.startswith('<'):
                # Remove HTML tags if any
                line = re.sub(r'<[^>]+>', '', line)
                if line:
                    lines.append(line)
        
        return '\n'.join(lines) if lines else None
    
    # Try manual subtitles first
    if subtitles_dict:
        for lang in ['pt', 'en', 'es', 'fr', 'de']:
            if lang in subtitles_dict:
                subtitle_data = subtitles_dict[lang]
                if subtitle_data and len(subtitle_data) > 0:
                    for subtitle_format in subtitle_data:
                        if 'url' in subtitle_format:
                            try:
                                response = requests.get(subtitle_format['url'], timeout=10)
                                if response.status_code == 200:
                                    text = parse_subtitle_content(response.text)
                                    if text:
                                        return text
                            except Exception as e:
                                continue
    
    # Try automatic captions if manual subtitles not found
    if automatic_captions_dict:
        for lang in ['pt', 'en', 'es', 'fr', 'de']:
            if lang in automatic_captions_dict:
                caption_data = automatic_captions_dict[lang]
                if caption_data and len(caption_data) > 0:
                    for caption_format in caption_data:
                        if 'url' in caption_format:
                            try:
                                response = requests.get(caption_format['url'], timeout=10)
                                if response.status_code == 200:
                                    text = parse_subtitle_content(response.text)
                                    if text:
                                        return text
                            except Exception as e:
                                continue
    
    return None

# Initialize session state for results
if "transcript" not in st.session_state:
    st.session_state.transcript = None
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "video_info" not in st.session_state:
    st.session_state.video_info = None

# Create tabs
tab1, tab2, tab3 = st.tabs(["🔗 YouTube Link", "📋 Prompt", "📊 Results"])

ydl_opts = {
    'skip_download': True,        # Não baixa o vídeo
    'writesubtitles': True,       # Baixa as legendas feitas por humanos
    'writeautomaticsub': True,   # Baixa as legendas automáticas (se as manuais não existirem)
    'subtitleslangs': ['pt', 'en'], # Idiomas desejados (ex: português e inglês)
    'subtitlesformat': 'srt',     # Formato de saída preferencial
    'outtmpl': '%(title)s.%(ext)s', # Nome do arquivo de saída
}

# Tab 1: YouTube Link Input
with tab1:
    st.subheader("📹 Enter YouTube Video")
    video_url = st.text_input("Paste the YouTube video URL here:")
    
    if video_url:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                title = info.get('title', 'No Title Found')
                thumbnail = info.get('thumbnail')
                
                st.session_state.video_info = {
                    'title': title,
                    'thumbnail': thumbnail,
                    'url': video_url
                }

            st.subheader(f"📺 {title}")
            st.image(thumbnail, use_container_width=True)

            if st.button("Process Video", key="process_video"):
                with st.status("Processing...", expanded=True) as status:
                    # Extract subtitles
                    st.write("Extracting subtitles...")
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(video_url, download=False)
                        subtitles = info.get('subtitles', {})
                        automatic_captions = info.get('automatic_captions', {})
                    
                    # Extract subtitle text (try manual first, then automatic)
                    subtitle_text = extract_subtitle_text(subtitles, automatic_captions)
                    
                    if not subtitle_text:
                        st.error("No subtitles or automatic captions found for this video.")
                    else:
                        st.session_state.transcript = subtitle_text
                        
                        # Display extracted subtitles
                        st.success("✅ Subtitles extracted successfully!")
                        st.divider()
                        st.subheader("📝 Extracted Subtitles")
                        st.text_area(
                            "Subtitle Content",
                            value=subtitle_text,
                            height=300,
                            disabled=True,
                            label_visibility="collapsed"
                        )
                        st.divider()
                        
                        # Analysis with selected model
                        st.write(f"Analyzing subtitles with {model}...")
                        
                        try:
                            if model == "gemini-3-flash-preview":
                                # Use Google Gemini
                                gemini_model = genai.GenerativeModel('gemini-3-flash-preview')
                                full_prompt = f"{prompt_template}\n\nSubtitles:\n{subtitle_text}\nYour answer should only include the game's final score and goals, as requested in the prompt."
                                gemini_response = gemini_model.generate_content(full_prompt)
                                st.session_state.analysis = gemini_response.text
                            else:
                                analysis_model = "gpt-4o-mini"
                                
                                response = client.chat.completions.create(
                                    model=analysis_model,
                                    messages=[
                                        {"role": "system", "content": "You are a helpful research assistant."},
                                        {"role": "user", "content": f"{prompt_template}\n\nSubtitles:\n{subtitle_text}\nYour answer should only include the game's final score and goals, as requested in the prompt."},
                                    ]
                                )
                                st.session_state.analysis = response.choices[0].message.content
                            
                            status.update(label="Analysis Complete!", state="complete")
                            st.success("Video processed successfully! Check the Results tab for the analysis.")
                        
                        except Exception as e:
                            st.error(f"Error during analysis: {str(e)}")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Tab 2: Prompt Display
with tab2:
    st.subheader(f"📋 {selected_prompt_name} Prompt")
    st.info("Selected prompt template:")
    st.text_area(
        "Prompt Content",
        value=prompt_template,
        height=400,
        disabled=True,
        label_visibility="collapsed"
    )

# Tab 3: Results
with tab3:
    st.subheader("📊 Processing Results")
    
    if st.session_state.transcript is None or st.session_state.analysis is None:
        st.info("No results yet. Process a video in the 'YouTube Link' tab to see results here.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Extracted Subtitles")
            st.text_area(
                "Subtitle Content",
                value=st.session_state.transcript,
                height=400,
                disabled=True,
                label_visibility="collapsed"
            )
        
        with col2:
            st.subheader(f"💡 Results Analysis")
            st.text_area(
                "Analysis Content",
                value=st.session_state.analysis,
                height=400,
                disabled=True,
                label_visibility="collapsed"
            )