# Script2Sound
Convert text scripts to natural-sounding audio using Google Cloud TTS

## 🚀 Deployment

### Backend Deployment (Google Cloud Run)
The backend is deployed on Google Cloud Platform using Cloud Run.

**Deployed Backend URL**: `https://script2sound-backend-678835024492.us-central1.run.app`

#### Backend Deployment Steps (Already Completed)
1. **Prerequisites**:
   - Google Cloud Project: `script2sound`
   - Service Account Key: `backend/app/credentials/script2sound-service_key.json` (not committed to repo)
   - Docker installed locally

2. **Build and Deploy**:
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

### Frontend Deployment (Streamlit Cloud)

1. **Push Code to GitHub**:
   ```bash
   git add .
   git commit -m "Update frontend for production"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select `streamlit_app.py` as the main file path
   - In the app settings, add the following secret:
     ```
     API_BASE_URL = "https://script2sound-backend-678835024492.us-central1.run.app"
     ```
   - Click "Deploy"

3. **Verify Deployment**:
   - Once deployed, test the app to ensure it connects to the backend and generates audio.

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run backend locally (optional)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Run frontend locally
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
- **Deployment**: Streamlit Cloud + Google Cloud Run

### Security Notes
- Google Cloud credentials are stored securely in the backend container and not exposed in the repository.
- Secrets are managed via `.streamlit/secrets.toml` locally and Streamlit Cloud secrets for production.
