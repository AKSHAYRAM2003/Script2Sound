# 🎤 Script2Sound

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://script2sound.streamlit.app)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Transform your text scripts into natural-sounding audio with advanced voice synthesis technology.**

Script2Sound is a modern web application that converts text scripts into high-quality, natural-sounding audio using Google Cloud's Neural2 Text-to-Speech technology. Perfect for content creators, educators, podcasters, and anyone who needs professional voice synthesis.

## ✨ Features
![Script2Sound Demo](./Screenshot%202025-09-06%20at%209.08.01 PM.png)

**Key Features:**

### 🎭 Advanced Voice Synthesis
- **Neural2 Voices**: Access to Google's most advanced TTS voices
- **Multiple Languages**: Support for various languages and accents
- **Voice Selection**: Choose from male and female voices with different characteristics
- **Natural Prosody**: Advanced intonation and speech patterns

### 🎵 Audio Customization
- **Speaking Rate Control**: Adjust speed from 0.5x to 2.0x
- **Pitch Adjustment**: Fine-tune voice pitch (-10 to +10)
- **SSML Support**: Enable Speech Synthesis Markup Language for enhanced naturalness
- **Voice Presets**: Pre-configured settings for different content types:
  - 🎭 **Storytelling**: Warm, engaging narration
  - 📊 **Presentation**: Clear, professional delivery
  - 📖 **Narration**: Authoritative, confident tone
  - 💬 **Conversational**: Friendly, natural conversation

### 🚀 Production Ready
- **Cloud Deployment**: Fully deployed on Google Cloud Run + Streamlit Cloud
- **Scalable Architecture**: FastAPI backend with async processing
- **Secure**: Credentials managed securely, no secrets in repository
- **High Availability**: 99.9% uptime with Google Cloud infrastructure

### 💾 Audio Management
- **MP3 Download**: High-quality audio export
- **Real-time Preview**: Listen before downloading
- **Session Management**: Keep audio in browser session
- **Character Limits**: Support for up to 10,000 characters

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/JSON    ┌─────────────────┐
│   Streamlit     │◄──────────────►│     FastAPI      │
│   Frontend      │                 │     Backend     │
│                 │                 │                 │
│ • Voice Config  │                 │ • Google TTS    │
│ • Audio Preview │                 │ • Audio Gen     │
│ • Download      │                 │ • Health Check  │
└─────────────────┘                 └─────────────────┘
         │                                   │
         └────────────► Streamlit Cloud ◄────┘
                             GCP Cloud Run
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Cloud Project (for backend deployment)
- GitHub account (for frontend deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/AKSHAYRAM2003/Script2Sound.git
   cd Script2Sound
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Open your browser**
   - Navigate to `http://localhost:8501`

## 📋 Usage

### Basic Text-to-Speech
1. Enter your text in the input area (max 10,000 characters)
2. Select your preferred voice from the sidebar
3. Adjust speaking rate and pitch if desired
4. Click "🎵 Generate Audio"
5. Preview and download your audio

### Advanced Features
- **Voice Presets**: Choose from Storytelling, Presentation, Narration, or Conversational
- **SSML Mode**: Enable for more natural speech patterns
- **Real-time Settings**: Adjust parameters and regenerate instantly

## 🔧 API Documentation

### Backend Endpoints

#### GET `/voices`
Returns available TTS voices.

**Response:**
```json
[
  {
    "name": "en-US-Neural2-A",
    "language_code": "en-US",
    "gender": "MALE",
    "natural_sample_rate": 24000
  }
]
```

#### POST `/generate-audio`
Generate audio from text.

**Request:**
```json
{
  "text": "Hello, world!",
  "voice_name": "en-US-Neural2-D",
  "language_code": "en-US",
  "speaking_rate": 1.0,
  "pitch": 0.0,
  "is_ssml": false
}
```

**Response:** Audio file (MP3)

#### GET `/health`
Health check endpoint.

## 🏭 Deployment

### Backend (Google Cloud Run)
The backend is pre-deployed at:
`https://script2sound-backend-678835024492.us-central1.run.app`

### Frontend (Streamlit Cloud)
The frontend is deployed at:
`https://script2sound.streamlit.app`

### Manual Deployment

#### Backend Deployment
```bash
# Set GCP project
gcloud config set project script2sound

# Build and push Docker image
gcloud builds submit --tag gcr.io/script2sound/script2sound-backend .

# Deploy to Cloud Run
gcloud run deploy script2sound-backend \
  --image gcr.io/script2sound/script2sound-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/script2sound-service_key.json
```

#### Frontend Deployment
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Set main file: `streamlit_app.py`
5. Add secret: `API_BASE_URL = "https://script2sound-backend-678835024492.us-central1.run.app"`
6. Deploy

## 🛠️ Development

### Project Structure
```
Script2Sound/
├── streamlit_app.py          # Main Streamlit application
├── requirements.txt          # Python dependencies
├── backend/
│   ├── Dockerfile           # Backend container config
│   ├── requirements.txt     # Backend dependencies
│   ├── app/
│   │   ├── main.py         # FastAPI application
│   │   ├── tts_service.py  # TTS service logic
│   │   └── credentials/    # GCP credentials (not committed)
│   └── streamlit_app.py    # Alternative frontend
├── .streamlit/
│   └── secrets.toml        # Local secrets
├── .gitignore              # Git ignore rules
└── README.md              # This file
```

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Testing
```bash
# Run backend tests
cd backend
python -m pytest

# Run frontend locally
streamlit run streamlit_app.py
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation
- Ensure all tests pass

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Cloud TTS**: For providing advanced text-to-speech technology
- **Streamlit**: For the amazing web app framework
- **FastAPI**: For the high-performance backend framework
- **Google Cloud Run**: For reliable container deployment

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/AKSHAYRAM2003/Script2Sound/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AKSHAYRAM2003/Script2Sound/discussions)
- **Email**: For business inquiries or support

---

**Made with ❤️ using Google Cloud, Streamlit, and FastAPI**
