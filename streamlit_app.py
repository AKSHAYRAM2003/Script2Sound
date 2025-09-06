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

# API base URL - update this with your deployed backend URL
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://127.0.0.1:8000")

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

def generate_audio(text: str, voice_name: str, language_code: str, speaking_rate: float, pitch: float, use_ssml: bool = False):
    """Generate audio using the API with enhanced options"""
    try:
        # Add SSML tags for more natural speech if enabled
        if use_ssml:
            # Wrap text in SSML for better prosody
            ssml_text = f"""<?xml version="1.0"?>
<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.w3.org/2001/10/synthesis
                   http://www.w3.org/TR/speech-synthesis11/synthesis.xsd"
       xml:lang="{language_code}">
    <prosody rate="{speaking_rate}" pitch="{pitch}st">
        {text}
    </prosody>
</speak>"""
            payload = {
                "text": ssml_text,
                "voice_name": voice_name,
                "language_code": language_code,
                "speaking_rate": 1.0,  # Let SSML control rate
                "pitch": 0.0,  # Let SSML control pitch
                "is_ssml": True
            }
        else:
            payload = {
                "text": text,
                "voice_name": voice_name,
                "language_code": language_code,
                "speaking_rate": speaking_rate,
                "pitch": pitch,
                "is_ssml": False
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
    st.title("🎤 Script2Sound - Enhanced Voice Interface")
    st.markdown("Convert your text scripts to natural-sounding audio")
    
    # Sidebar for settings
    with st.sidebar:
        st.header("🎭 Voice Settings")
        
        # Voice selection with more options
        voices = get_available_voices()
        if voices:
            # Group voices by gender for better UX
            male_voices = [v for v in voices if v.get('gender') == 'MALE']
            female_voices = [v for v in voices if v.get('gender') == 'FEMALE']
            
            st.subheader("Male Voices")
            male_options = [f"{v['name']} ({v['language_code']})" for v in male_voices]
            if male_options:
                selected_male = st.selectbox("Select Male Voice", male_options, key="male")
                male_voice = male_voices[male_options.index(selected_male)]['name']
            else:
                male_voice = None
            
            st.subheader("Female Voices") 
            female_options = [f"{v['name']} ({v['language_code']})" for v in female_voices]
            if female_options:
                selected_female = st.selectbox("Select Female Voice", female_options, key="female")
                female_voice = female_voices[female_options.index(selected_female)]['name']
            else:
                female_voice = None
            
            # Voice type selection
            voice_type = st.radio("Voice Type", ["Male", "Female"], index=0)
            if voice_type == "Male" and male_voice:
                selected_voice = male_voice
            elif voice_type == "Female" and female_voice:
                selected_voice = female_voice
            else:
                selected_voice = "en-US-Neural2-D"  # fallback
        else:
            selected_voice = "en-US-Neural2-D"
            st.warning("Could not load voices, using default")
        
        st.markdown("---")
        st.header("🎵 Audio Settings")
        
        # Enhanced audio controls
        speaking_rate = st.slider("Speaking Rate", 0.5, 2.0, 1.0, 0.1, 
                                help="1.0 = normal speed, 0.5 = slower, 2.0 = faster")
        pitch = st.slider("Pitch", -10.0, 10.0, 0.0, 1.0,
                         help="0 = normal pitch, positive = higher, negative = lower")
        
        # SSML option
        use_ssml = st.checkbox("Use SSML for Natural Prosody", value=True,
                              help="Enables better intonation and natural speech patterns")
        
        # Preset configurations for common scenarios
        st.markdown("---")
        st.subheader("🎯 Quick Presets")
        preset = st.selectbox("Voice Presets", 
                            ["Default", "Storytelling", "Presentation", "Narration", "Conversational"])
        
        if preset == "Storytelling":
            speaking_rate = 0.9
            pitch = -2.0
            selected_voice = "en-US-Neural2-D"  # Warm voice
        elif preset == "Presentation":
            speaking_rate = 1.1
            pitch = 1.0
            selected_voice = "en-US-Neural2-C"  # Clear voice
        elif preset == "Narration":
            speaking_rate = 0.95
            pitch = -1.0
            selected_voice = "en-US-Neural2-F"  # Authoritative voice
        elif preset == "Conversational":
            speaking_rate = 1.05
            pitch = 0.5
            selected_voice = "en-US-Neural2-E"  # Friendly voice
        
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
        st.subheader("📝 Text Input")
        text_input = st.text_area(
            "Enter your script (max 10,000 characters)",
            height=300,
            max_chars=10000,
            placeholder="Paste your text here... Try different voices and settings for natural sound!"
        )
        
        # Character count with visual indicator
        char_count = len(text_input)
        if char_count > 8000:
            st.error(f"Characters: {char_count}/10,000 (approaching limit)")
        elif char_count > 5000:
            st.warning(f"Characters: {char_count}/10,000")
        else:
            st.caption(f"Characters: {char_count}/10,000")
        
        # Generate button with enhanced feedback
        if st.button("🎵 Generate Audio", type="primary", use_container_width=True):
            if not text_input.strip():
                st.error("Please enter some text")
            elif char_count > 10000:
                st.error("Text is too long (max 10,000 characters)")
            else:
                with st.spinner("Generating natural-sounding audio..."):
                    audio_data = generate_audio(
                        text_input, 
                        selected_voice, 
                        "en-US",
                        speaking_rate, 
                        pitch,
                        use_ssml
                    )
                    
                    if audio_data:
                        st.success("🎉 Audio generated successfully!")
                        # Store audio in session state
                        st.session_state.audio_data = audio_data
                        st.session_state.audio_generated = True
                        st.session_state.current_settings = {
                            "voice": selected_voice,
                            "rate": speaking_rate,
                            "pitch": pitch,
                            "ssml": use_ssml
                        }
    
    with col2:
        st.subheader("🎧 Audio Output")
        
        if 'audio_generated' in st.session_state and st.session_state.audio_generated:
            # Display current settings
            if 'current_settings' in st.session_state:
                settings = st.session_state.current_settings
                st.info(f"**Voice:** {settings['voice']}\n**Rate:** {settings['rate']}\n**Pitch:** {settings['pitch']}\n**SSML:** {settings['ssml']}")
            
            # Display audio player
            audio_bytes = st.session_state.audio_data
            st.audio(audio_bytes, format="audio/mp3")
            
            # Download button
            st.download_button(
                label="📥 Download MP3",
                data=audio_bytes,
                file_name="natural_audio.mp3",
                mime="audio/mpeg",
                use_container_width=True
            )
            
            # Clear button
            if st.button("🗑️ Clear", use_container_width=True):
                if 'audio_data' in st.session_state:
                    del st.session_state.audio_data
                if 'audio_generated' in st.session_state:
                    del st.session_state.audio_generated
                if 'current_settings' in st.session_state:
                    del st.session_state.current_settings
                st.rerun()
        else:
            st.info("Generate audio to see it here")
            
            # Tips for natural sound
            with st.expander("💡 Tips for Natural Sound"):
                st.markdown("""
                - **Try different voices**: Male vs Female, different Neural2 variants
                - **Adjust speaking rate**: 0.8-1.2 for natural conversation
                - **Use SSML**: Enables better intonation
                - **Experiment with presets**: Each optimized for different content types
                - **Pitch adjustment**: Slight variations (-2 to +2) can sound more human
                """)
    
    # Footer
    st.markdown("---")
    st.caption("Script2Sound - Enhanced with Natural Voice Technology")

if __name__ == "__main__":
    main()