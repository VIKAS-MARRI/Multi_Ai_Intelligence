# Jarvis Multi-AI Voice Assistant

## 🚀 Enterprise-Grade Multi-AI Voice Assistant with Professional Dashboard

A production-ready, enterprise-class AI assistant that harnesses the power of multiple AI models (OpenAI ChatGPT, Google Gemini, and DeepSeek) with an intelligent fusion engine, voice capabilities, and a modern, professional dashboard.

### ✨ Features

- **Multi-AI Integration**
  - OpenAI ChatGPT API
  - Google Gemini API
  - DeepSeek API
  - Concurrent querying for optimal performance

- **Intelligent Fusion Engine**
  - Combines responses from multiple AI providers
  - Removes duplicate information
  - Creates coherent, professional answers
  - Confidence scoring

- **Voice Capabilities**
  - Speech-to-text (STT) using Google Speech Recognition
  - Text-to-speech (TTS) with pyttsx3 and edge-tts support
  - Real-time audio playback

- **Professional Dashboard**
  - Modern glassmorphism UI design
  - Smooth animations and transitions
  - Real-time response updates
  - Responsive design (mobile + desktop)
  - Dark theme optimized for enterprise use

- **Enterprise Architecture**
  - Modular service-based design
  - Environment variable configuration
  - Comprehensive error handling
  - Logging system
  - API-first architecture
  - Async/await support

---

## 📋 Project Structure

```
jarvis2.0/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main_routes.py       # Main page & health check
│   │   └── ai_routes.py         # AI query & voice endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── openai_service.py    # ChatGPT integration
│   │   ├── gemini_service.py    # Gemini integration
│   │   ├── deepseek_service.py  # DeepSeek integration
│   │   ├── fusion_service.py    # Intelligent fusion engine
│   │   └── voice_service.py     # Speech-to-text & text-to-speech
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css        # Professional styling
│   │   ├── js/
│   │   │   └── app.js           # Frontend logic
│   │   └── audio/               # Generated audio files
│   └── templates/
│       └── index.html           # Dashboard UI
├── config.py                     # Configuration management
├── run.py                        # Application entry point
├── .env                         # Environment variables (local development)
├── .env.example                 # Environment template
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## 🔧 Installation & Setup

### Prerequisites

- Python 3.11+
- pip (Python package manager)
- Microphone (for voice input)
- API keys for:
  - OpenAI (ChatGPT)
  - Google Gemini
  - DeepSeek

### Step 1: Clone/Download Project

```bash
cd jarvis2.0
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** If you encounter issues with PyAudio on Windows, you may need to install it separately:
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```

### Step 4: Configure Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Google Gemini Configuration
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-pro

# DeepSeek Configuration
DEEPSEEK_API_KEY=your-deepseek-api-key-here
DEEPSEEK_MODEL=deepseek-chat

# Voice Configuration (Optional)
VOICE_ENGINE=pyttsx3      # or edge-tts
VOICE_RATE=150
VOICE_VOLUME=1.0

# Application Configuration
FLASK_ENV=development
FLASK_DEBUG=true
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

### Step 5: Run Application

```bash
python run.py
```

The application will start at: `http://localhost:5000`

---

## 🎯 How to Use

### 1. **Text Input Query**
   - Type your question in the text area
   - Click "Ask AI" or press Ctrl+Enter
   - Wait for responses from all AI models
   - View the fused response in the main card

### 2. **Voice Input Query**
   - Click "Voice Input" button
   - Speak your question clearly
   - The system will automatically process your query once you stop speaking

### 3. **Audio Output**
   - Click the "Speak" button in the Fused Response section
   - The system will convert the response to speech and play it

### 4. **Enable/Disable Fusion**
   - Toggle the "Enable Fusion" checkbox
   - When enabled: Shows intelligent combined response
   - When disabled: Shows individual responses from each provider

### 5. **Clear**
   - Click "Clear" to reset the interface

---

## 📡 API Endpoints

### Query Endpoint

**POST** `/api/query`

Request:
```json
{
  "prompt": "Your question here",
  "max_tokens": 1000,
  "enable_fusion": true
}
```

Response:
```json
{
  "status": "success",
  "query": "Your question here",
  "responses": {
    "openai": {
      "status": "success",
      "provider": "openai",
      "response": "ChatGPT response..."
    },
    "gemini": {
      "status": "success",
      "provider": "gemini",
      "response": "Gemini response..."
    },
    "deepseek": {
      "status": "success",
      "provider": "deepseek",
      "response": "DeepSeek response..."
    }
  },
  "fused_response": {
    "status": "success",
    "fused_response": "Intelligent combined response...",
    "confidence": 0.95,
    "num_providers": 3
  }
}
```

### Text-to-Speech Endpoint

**POST** `/api/text-to-speech`

Request:
```json
{
  "text": "Text to convert to speech"
}
```

Response:
```json
{
  "status": "success",
  "audio_url": "/static/audio/response.mp3",
  "engine": "pyttsx3"
}
```

### Providers Status Endpoint

**GET** `/api/providers`

Response:
```json
{
  "providers": [
    {
      "name": "openai",
      "display_name": "ChatGPT",
      "configured": true
    },
    {
      "name": "gemini",
      "display_name": "Google Gemini",
      "configured": true
    },
    {
      "name": "deepseek",
      "display_name": "DeepSeek",
      "configured": true
    }
  ]
}
```

---

## 🏗️ Architecture

### Three-Layer Architecture

```
┌─────────────────────────────────────┐
│   PRESENTATION LAYER                │
│   - HTML/CSS/JavaScript             │
│   - Dashboard UI                    │
│   - Real-time Updates               │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   API LAYER                         │
│   - Flask Routes/Blueprints         │
│   - Request Validation              │
│   - Response Formatting             │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   SERVICE LAYER                     │
│   - AI Service Integration          │
│   - Fusion Engine                   │
│   - Voice Processing                │
│   - Business Logic                  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   EXTERNAL SERVICES                 │
│   - OpenAI API                      │
│   - Google Gemini API               │
│   - DeepSeek API                    │
│   - Speech Recognition              │
└─────────────────────────────────────┘
```

### Async Processing

- All AI model queries run **concurrently** using `asyncio.gather()`
- Non-blocking I/O for optimal performance
- Timeout handling for reliabilityT

---

## 🔐 Security Features

- ✅ API keys stored in `.env` (never in code)
- ✅ Input validation and sanitization
- ✅ CORS configuration
- ✅ Secure session cookies
- ✅ Environment-specific configurations
- ✅ Error message masking in production

---

## 🚀 Deployment

### Production Deployment

```bash
# Install production dependencies
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Environment Setup for Production

Create `.env` with production settings:

```env
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your-secure-random-key-here
SESSION_COOKIE_SECURE=true

# API Keys (use secure storage in production: AWS Secrets Manager, Azure Key Vault, etc.)
OPENAI_API_KEY=...
GEMINI_API_KEY=...
DEEPSEEK_API_KEY=...
```

### Docker Deployment (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=run.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

Build and run:

```bash
docker build -t jarvis .
docker run -p 5000:5000 --env-file .env jarvis
```

---

## 🧪 Development

### Run Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black app/ config.py run.py

# Lint
flake8 app/ config.py run.py

# Type checking
mypy app/ config.py run.py
```

---

## 📊 Performance Considerations

- **Concurrent Queries**: 3 AI models queried simultaneously (~1-2 seconds)
- **Response Fusion**: Deduplication engine processes responses instantly
- **Caching**: Implement Redis for frequent queries (production)
- **Rate Limiting**: Configure API rate limits per provider
- **Timeout**: Default 30 seconds per API call

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'app'"
**Solution**: Ensure you're running from the project root directory

### Issue: "Speech Recognition not available"
**Solution**: Install PyAudio:
```bash
pip install pipwin
pipwin install pyaudio
```

### Issue: API Key errors
**Solution**: 
1. Verify keys in `.env` file
2. Ensure keys have proper permissions
3. Check API usage limits

### Issue: Port already in use
**Solution**: Change port in `.env`:
```env
FLASK_PORT=5001
```

---

## 📈 Future Enhancements

- [ ] Response caching with Redis
- [ ] User authentication & profiles
- [ ] Response history & analytics
- [ ] Custom prompts & templates
- [ ] Multi-language support
- [ ] Advanced voice features
- [ ] Mobile app (React Native)
- [ ] Real-time WebSocket updates
- [ ] Response streaming
- [ ] Custom model fine-tuning

---

## 📞 Support

For issues, questions, or contributions:

1. Check existing issues
2. Verify configuration (.env file)
3. Check logs for detailed error messages
4. Ensure all dependencies are installed

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- OpenAI for ChatGPT API
- Google for Gemini API
- DeepSeek for DeepSeek API
- Flask for the web framework
- TailwindCSS for UI utilities

---

## 📞 Contact & Support

For enterprise support or custom implementations, contact the development team.

---

**Jarvis Multi-AI Voice Assistant** - *Powered by Enterprise-Grade AI Intelligence*

Version: 1.0.0
Last Updated: 2024
