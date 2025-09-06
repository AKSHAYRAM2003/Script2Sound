# Script2Sound
Convert text scripts to natural-sounding audio using Google Cloud TTS

## 🚀 Deployment on Streamlit Cloud

### Prerequisites
1. **Deploy Backend First**: Deploy your FastAPI backend to a service like:
   - Railway
   - Heroku
   - Vercel
   - Render
   - DigitalOcean App Platform

2. **Get Backend URL**: Note the deployed backend URL (e.g., `https://your-backend.herokuapp.com`)

### Streamlit Cloud Deployment Steps

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select `streamlit_app.py` as the main file
   - Add your backend URL to secrets:
     ```
     API_BASE_URL = "https://your-deployed-backend-url.com"
     ```

3. **Set Environment Variables** (if needed):
   - In Streamlit Cloud dashboard, add any required environment variables

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run streamlit_app.py
```

### Features
- 🎤 Multiple voice options (Neural2 voices)
- 🎵 Adjustable speaking rate and pitch
- 📝 Text-to-speech conversion (up to 10,000 characters)
- 📥 Audio download in MP3 format
- 🎯 Voice presets for different content types

### Tech Stack
- **Frontend**: Streamlit
- **Backend**: FastAPI + Google Cloud TTS
- **Deployment**: Streamlit Cloud + [Your Backend Host]
