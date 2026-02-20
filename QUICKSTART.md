# 🚀 Quick Start Guide - Jarvis Multi-AI Voice Assistant

## Getting Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure API Keys
Open `.env` and add your API keys:
```env
OPENAI_API_KEY=sk-your-key-here
GEMINI_API_KEY=your-key-here
DEEPSEEK_API_KEY=your-key-here
```

### Step 3: Run the Application
```bash
python run.py
```

### Step 4: Open Dashboard
Visit: **http://localhost:5000**

---

## 🎯 Basic Usage

### Text Query
1. Type your question in the text area
2. Click "Ask AI" or press Ctrl+Enter
3. View responses from all AI models
4. See the fused intelligent response

### Voice Query
1. Click "Voice Input"
2. Speak your question
3. System processes automatically
4. View AI responses

### Audio Response
1. Click "Speak" button
2. Listen to the fused response
3. Audio plays in browser

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `config.py` | Configuration settings |
| `run.py` | Start the app |
| `.env` | API keys (create from .env.example) |
| `app/` | All application code |
| `README.md` | Full documentation |

---

## 🔑 Required API Keys

1. **OpenAI** (ChatGPT)
   - Get from: https://platform.openai.com/api-keys
   - Format: `sk-...`

2. **Google Gemini**
   - Get from: https://ai.google.dev/
   - Format: API key

3. **DeepSeek**
   - Get from: https://platform.deepseek.com
   - Format: API key

---

## ⚙️ Environment Variables

```env
# Flask Settings
FLASK_ENV=development
FLASK_DEBUG=true
FLASK_PORT=5000

# API Keys (Required)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
DEEPSEEK_API_KEY=...

# Voice Settings
VOICE_ENGINE=pyttsx3
VOICE_RATE=150
VOICE_VOLUME=1.0

# API Timeouts
API_TIMEOUT=30
```

---

## 🐛 Troubleshooting

### ModuleNotFoundError
```bash
# Make sure you run from project root directory
cd jarvis2.0
```

### API Key Error
```bash
# Verify .env file exists and has keys
# Restart the application
python run.py
```

### Port Already in Use
```bash
# Change port in .env
FLASK_PORT=5001
```

### Speech Recognition Not Working
```bash
# Install audio library
pip install pyaudio
```

---

## 📊 File Structure

```
jarvis2.0/
├── app/
│   ├── routes/             # API endpoints
│   ├── services/           # AI integrations & fusion
│   ├── static/             # CSS & JavaScript
│   └── templates/          # HTML dashboard
├── config.py              # Configuration
├── run.py                 # Start application
├── .env                   # Your API keys (create from .env.example)
├── requirements.txt       # Dependencies
└── README.md             # Full documentation
```

---

## 🔗 Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Dashboard |
| `/api/query` | POST | Query all AI models |
| `/api/text-to-speech` | POST | Convert text to audio |
| `/api/providers` | GET | Check provider status |
| `/health` | GET | Health check |

---

## 🎨 Features

✨ **Multi-AI**: Query 3 AI models simultaneously
🔀 **Fusion**: Intelligent response combining
🎤 **Voice**: Speech-to-text input
🔊 **Audio**: Text-to-speech output
🎯 **Professional UI**: Modern, responsive dashboard
⚡ **Fast**: ~1-2 second processing time

---

## 📌 Tips

- **Ctrl+Enter**: Quick submit text query
- **Voice Button**: Hands-free input
- **Speak Button**: Listen to response
- **Clear Button**: Reset interface
- **Fusion Toggle**: Enable/disable response combining

---

## 🚀 Next Steps

1. ✅ Install dependencies
2. ✅ Add API keys to `.env`
3. ✅ Run `python run.py`
4. ✅ Open http://localhost:5000
5. ✅ Ask a question!

---

## 📚 More Information

- Full docs: See `README.md`
- Implementation details: See `IMPLEMENTATION_SUMMARY.md`
- Code comments: All files have inline documentation

---

**Ready to use? Start with: `python run.py`**
