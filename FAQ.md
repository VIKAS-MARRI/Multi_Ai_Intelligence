# ❓ Frequently Asked Questions (FAQ)

## General Questions

### Q: Can I use this in production?
**A:** Yes! This is a production-ready, enterprise-grade application. It follows industry best practices, includes error handling, logging, and security measures. See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for production deployment.

### Q: What Python version do I need?
**A:** Python 3.11 or higher. We use async/await features and modern Python syntax.

### Q: Can I use this commercially?
**A:** Yes, it's MIT licensed. You can use, modify, and distribute it for commercial purposes.

### Q: How much do the AI APIs cost?
**A:** Pricing varies by provider:
- **OpenAI**: Pay-per-token (usually $0.001-$0.03 per 1K tokens)
- **Google Gemini**: Free tier + paid options
- **DeepSeek**: Free tier + paid options

### Q: Does it work offline?
**A:** No, all AI models require internet connectivity. Voice recognition uses Google's service, which also requires internet.

---

## Installation & Setup

### Q: I'm getting "ModuleNotFoundError: No module named 'openai'"
**A:** Run: `pip install -r requirements.txt`

### Q: Installation fails on Windows
**A:** For PyAudio issues, try:
```bash
pip install pipwin
pipwin install pyaudio
```

### Q: How do I get API keys?
**A:** 
- **OpenAI**: https://platform.openai.com/api-keys
- **Google Gemini**: https://ai.google.dev/
- **DeepSeek**: https://platform.deepseek.com/

### Q: Where do I put my API keys?
**A:** Create a `.env` file in the project root and add:
```env
OPENAI_API_KEY=sk-your-key-here
GEMINI_API_KEY=your-key-here
DEEPSEEK_API_KEY=your-key-here
```

### Q: What if I don't have all three API keys?
**A:** That's fine! The app handles missing keys gracefully. It will show an error for unavailable providers but still work with the ones you have configured.

### Q: Port 5000 is already in use
**A:** Edit `.env`:
```env
FLASK_PORT=5001
```

---

## Usage & Features

### Q: Why is the response slow?
**A:** The system queries 3 AI models concurrently, which takes 1-2 seconds per API call plus network latency. This is normal.

### Q: Can I query just one AI model?
**A:** Currently, the app queries all three simultaneously. You can disable fusion to see individual responses, or modify the code to select specific providers.

### Q: How many characters can I enter?
**A:** Maximum 5000 characters per prompt.

### Q: Does voice input work on all browsers?
**A:** No, browser Speech Recognition support varies:
- ✅ Chrome/Edge (full support)
- ✅ Safari (partial support)
- ❌ Firefox (limited support)

Fallback: Type or copy-paste text.

### Q: Can I save conversations?
**A:** Currently, no. Responses are temporary. To add this, implement database storage (PostgreSQL, MongoDB, etc.).

### Q: How do I hide my API keys?
**A:** They are already hidden in `.env` file, which is excluded from Git. Never commit `.env` to version control.

### Q: Can I edit the UI?
**A:** Absolutely! The UI is in `app/templates/index.html` and styled with `app/static/css/style.css`. JavaScript is in `app/static/js/app.js`.

---

## AI & Fusion Engine

### Q: How does the fusion engine work?
**A:** It:
1. Collects responses from all AI models
2. Extracts key sentences
3. Removes duplicate information
4. Combines into a coherent response
5. Calculates confidence score

See [app/services/fusion_service.py](app/services/fusion_service.py) for details.

### Q: Can I customize the fusion logic?
**A:** Yes! Modify `app/services/fusion_service.py` to change:
- Deduplication sensitivity
- Response combining strategy
- Length limits
- Confidence calculation

### Q: Which AI model is best?
**A:** They each have strengths:
- **ChatGPT**: General knowledge, well-rounded
- **Gemini**: Multimodal, creative
- **DeepSeek**: Technical, analytical

The fusion engine combines their strengths!

### Q: Can I add more AI models?
**A:** Yes! Create a new service in `app/services/`, implement the query method, and add it to `ai_routes.py`.

---

## Voice Features

### Q: Voice input not working
**A:** Check:
1. Microphone permissions enabled
2. Browser supports Speech Recognition
3. Internet connection active
4. Microphone is plugged in and recognized

### Q: Text-to-speech not working
**A:** Try:
1. Ensure `pyttsx3` is installed: `pip install pyttsx3`
2. Check audio output is not muted
3. Install system audio libraries

On Linux:
```bash
sudo apt-get install espeak ffmpeg libespeak1
```

### Q: Can I change the voice?
**A:** Yes, in `app/services/voice_service.py`, you can modify:
- Voice rate (speed)
- Voice volume
- Voice engine (pyttsx3 vs edge-tts)

### Q: Which TTS engine is better?
**A:** 
- **pyttsx3**: Offline, cross-platform, simple
- **edge-tts**: Online, natural-sounding, modern

### Q: Can I use a different language for voice?
**A:** Currently English only. To add language support:
1. Modify `speech_to_text()` language setting
2. Update TTS language configuration
3. Test with different locales

---

## Performance & Optimization

### Q: How can I make it faster?
**A:** 
1. Set higher timeouts in `.env` (servers might need more time)
2. Use edge-tts instead of pyttsx3
3. Add caching layer (Redis)
4. Use faster AI models (gpt-3.5-turbo vs gpt-4)
5. Implement response streaming

### Q: Can I cache responses?
**A:** Yes, with Redis:
```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis'})
```

### Q: How many concurrent users can it handle?
**A:** Depends on deployment:
- Local: ~10 users
- Single server: ~100 users
- Load-balanced: Scales with servers

### Q: What's the maximum response length?
**A:** Set in `.env`:
```
FUSION_MAX_LENGTH=2000  # characters
```

---

## Security

### Q: Are my API keys safe?
**A:** 
- ✅ Stored in `.env` (not in code)
- ✅ Not logged or displayed
- ✅ Not exposed in client-side code

Production best practice: Use AWS Secrets Manager, Azure Key Vault, or Google Secret Manager.

### Q: Can I use this behind a firewall?
**A:** Yes, but it needs internet for AI APIs. Configure firewall to allow outbound connections to:
- `api.openai.com`
- `generativelanguage.googleapis.com`
- `api.deepseek.com`

### Q: How do I run it on HTTPS?
**A:** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for SSL setup with Let's Encrypt.

### Q: Can I require user authentication?
**A:** The current version doesn't have auth. To add it:
1. Install Flask-Login: `pip install flask-login`
2. Implement authentication in `app/__init__.py`
3. Protect routes with `@login_required` decorator

### Q: Are requests encrypted?
**A:** Only if you use HTTPS. See deployment guide for setup.

---

## Troubleshooting

### Q: "Connection refused" error
**A:** The API isn't running. Run: `python run.py`

### Q: "No response from AI"
**A:** Check:
1. API keys are correct
2. API key has sufficient quota
3. Internet connection works
4. Firewall allows outbound connections

### Q: "CORS error" in browser
**A:** This is configured in `app/__init__.py`. For production, restrict CORS to your domain.

### Q: Application crashes on startup
**A:** Check logs:
```bash
python run.py  # See error messages
```

### Q: Responses are all the same
**A:** API keys might not be properly configured. Verify in `.env`.

### Q: Memory usage is high
**A:** Try:
1. Reduce number of concurrent requests
2. Clear audio cache: `rm -rf app/static/audio/*`
3. Implement garbage collection
4. Add memory limits in deployment

---

## Development

### Q: How do I modify the code?
**A:** The code is organized by function:
- **Routes**: `app/routes/`
- **Services**: `app/services/`
- **UI**: `app/templates/` + `app/static/`
- **Config**: `config.py`

### Q: Can I add custom AI providers?
**A:** Yes! Create a new service file and add endpoints in `ai_routes.py`.

### Q: How do I run tests?
**A:** 
```bash
pip install pytest
pytest
```

### Q: How do I contribute?
**A:** 
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Q: Can I use this as a template?
**A:** Yes! It's designed to be a starting point for custom AI applications.

---

## Deployment

### Q: How do I deploy to production?
**A:** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions covering:
- Local setup
- Gunicorn
- Nginx reverse proxy
- Docker
- AWS/Azure/GCP
- Systemd service

### Q: Which hosting provider should I use?
**A:** Popular options:
- **AWS**: EC2, Elastic Beanstalk, Lambda + API Gateway
- **Azure**: App Service, Container Instances
- **Google Cloud**: Cloud Run, Compute Engine
- **Heroku**: Simple, good for small projects
- **DigitalOcean**: Affordable VPS option

### Q: How do I update without downtime?
**A:** Use:
1. Blue-green deployment
2. Rolling deployment
3. Load balancer with multiple instances

### Q: Can I run it in a container?
**A:** Yes! Dockerfile is provided. See deployment guide.

### Q: How do I monitor the app?
**A:** Use:
- Application logs (`/var/log/jarvis/`)
- Prometheus + Grafana
- Datadog
- New Relic
- AWS CloudWatch

---

## Cost Considerations

### Q: What's the typical monthly cost?
**A:** Example for 1000 queries/month:
- **APIs**: $5-50 (depends on model + usage)
- **Hosting**: $5-50 (depends on choice)
- **Total**: $10-100/month

### Q: How can I reduce costs?
**A:** 
1. Use cheaper AI models
2. Implement caching
3. Use free tiers where possible
4. Optimize prompts for fewer tokens

### Q: Is there a free tier?
**A:** Yes:
- Most AI providers have free tiers
- Can host on free tier of cloud providers (limited)
- Open-source, no licensing costs

---

## Advanced Topics

### Q: How do I scale this?
**A:** 
1. Use load balancer
2. Run multiple instances
3. Use managed database
4. Implement caching
5. Use CDN for static files
6. Add message queue (Celery, RabbitMQ)

### Q: Can I use Kubernetes?
**A:** Yes! Create a Helm chart or deployment manifest.

### Q: How do I implement streaming responses?
**A:** Use Server-Sent Events (SSE) or WebSockets. Requires significant refactoring.

### Q: Can I run this on a Raspberry Pi?
**A:** Technically yes, but performance will be limited. AI API calls would be slow.

---

## Still Have Questions?

1. **Check Documentation**
   - [README.md](README.md) - Full guide
   - [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Architecture
   - [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Deployment

2. **Read Code Comments**
   - All files have inline documentation

3. **Check Inline Debugging**
   - Enable debug mode: `FLASK_DEBUG=true`
   - Check log files

4. **External Resources**
   - Flask: https://flask.palletsprojects.com/
   - OpenAI: https://platform.openai.com/docs/
   - Google Gemini: https://ai.google.dev/
   - DeepSeek: https://platform.deepseek.com/

---

**Last Updated**: February 2024  
**Version**: 1.0.0

*For more help, check the code comments and documentation files!*
