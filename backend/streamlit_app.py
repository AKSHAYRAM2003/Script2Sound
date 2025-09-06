import streamlit as st
import requests
import base64
from typing import List, Dict

# Configure page
st.set_page_config(
    page_title="Script2Sound - Test Interface",
    page_icon="🎤",
    layout="wide"
)

# API base URL
API_BASE_URL = "http://127.0.0.1:8000"

def get_available_voices() -> List[Dict]:
    """Fetch available voices from the API"""
    try:
        response = requests.get(f"{API_BASE_URL}/voices")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Failed to fetch voices: {e}")
        return []

def generate_audio(text: str, voice_name: str, language_code: str, speaking_rate: float, pitch: float):
    """Generate audio using the API"""
    try:
        payload = {
            "text": text,
            "voice_name": voice_name,
            "language_code": language_code,
            "speaking_rate": speaking_rate,
            "pitch": pitch
        }
        
        response = requests.post(f"{API_BASE_URL}/generate-audio", json=payload)
        
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Request failed: {e}")
        return None

def main():
    st.title("🎤 Script2Sound - Test Interface")
    st.markdown("Convert your text scripts to natural-sounding audio")
    
    # Sidebar for settings
    with st.sidebar:
        st.header("Settings")
        
        # Voice selection
        voices = get_available_voices()
        if voices:
            voice_options = [f"{voice['name']} ({voice['gender']})" for voice in voices]
            selected_voice_display = st.selectbox("Select Voice", voice_options)
            selected_voice = voices[voice_options.index(selected_voice_display)]['name']
        else:
            selected_voice = "en-US-Neural2-D"
            st.warning("Could not load voices, using default")
        
        # Audio settings
        speaking_rate = st.slider("Speaking Rate", 0.25, 4.0, 1.0, 0.25)
        pitch = st.slider("Pitch", -20.0, 20.0, 0.0, 1.0)
        
        st.markdown("---")
        st.markdown("**API Status:**")
        try:
            health_response = requests.get(f"{API_BASE_URL}/health")
            if health_response.status_code == 200:
                st.success("✅ Backend Connected")
            else:
                st.error("❌ Backend Error")
        except:
            st.error("❌ Cannot Connect to Backend")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Text Input")
        text_input = st.text_area(
            "Enter your script (max 10,000 characters)",
            height=300,
            max_chars=10000,
            placeholder="Paste your text here..."
        )
        
        # Character count
        char_count = len(text_input)
        st.caption(f"Characters: {char_count}/10,000")
        
        # Generate button
        if st.button("🎵 Generate Audio", type="primary", use_container_width=True):
            if not text_input.strip():
                st.error("Please enter some text")
            elif char_count > 10000:
                st.error("Text is too long (max 10,000 characters)")
            else:
                with st.spinner("Generating audio..."):
                    audio_data = generate_audio(
                        text_input, 
                        selected_voice, 
                        "en-US",
                        speaking_rate, 
                        pitch
                    )
                    
                    if audio_data:
                        st.success("Audio generated successfully!")
                        # Store audio in session state
                        st.session_state.audio_data = audio_data
                        st.session_state.audio_generated = True
    
    with col2:
        st.subheader("Audio Output")
        
        if 'audio_generated' in st.session_state and st.session_state.audio_generated:
            # Display audio player
            audio_bytes = st.session_state.audio_data
            st.audio(audio_bytes, format="audio/mp3")
            
            # Download button
            st.download_button(
                label="📥 Download MP3",
                data=audio_bytes,
                file_name="generated_audio.mp3",
                mime="audio/mpeg",
                use_container_width=True
            )
            
            # Clear button
            if st.button("🗑️ Clear", use_container_width=True):
                del st.session_state.audio_data
                del st.session_state.audio_generated
                st.rerun()
        else:
            st.info("Generate audio to see it here")
    
    # Footer
    st.markdown("---")
    st.caption("Script2Sound - Powered by Google Cloud TTS")

if __name__ == "__main__":
    main()