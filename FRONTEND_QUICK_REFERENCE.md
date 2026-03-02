# 🚀 Jarvis Frontend - Quick Reference

## File Locations

```
templates/index.html              Main HTML file
app/static/css/styles.css        All CSS styling (1020 lines)
app/static/js/script.js          All JavaScript logic (720 lines)
```

## Key Elements

### HTML Structure
- Sidebar with logo and provider status
- Chat area with message display
- Input area with microphone and send button
- Settings modal
- System messages and welcome screen

### CSS
- 1020 lines of modern dark theme styling
- Glassmorphism effects with backdrop blur
- Responsive breakpoints (desktop/tablet/mobile)
- CSS animations with GPU acceleration
- Custom scrollbar styling
- Gradient backgrounds and modern typography

### JavaScript
- 720 lines of vanilla JavaScript
- No external dependencies
- Message handling (send/receive/display)
- Voice input support (Web Speech API)
- Provider status management
- Settings persistence (localStorage)
- API integration with `/api/chat`
- Comprehensive error handling
- Debug utilities for testing

## Quick Start

### 1. Start Your Backend
```bash
python run.py
# or
python app.py
```

### 2. Open Browser
```
http://localhost:5000/
```

### 3. Test Chat
- Type a message → Press Enter
- Click microphone 🎤 → Speak → Send automatically
- Change settings ⚙️ for preferences

## API Integration

### Request Format
```json
POST /api/chat
{
  "message": "user input text",
  "conversation_id": "web-session",
  "provider": "auto"
}
```

### Expected Response
```json
{
  "response": "assistant output text",
  "provider": "gemini|openai|deepseek|fallback",
  "timestamp": "2026-02-21T10:30:00Z"
}
```

## Console Debug Commands

```javascript
// View application state
JarvisDebug.getState()

// View settings
JarvisDebug.getSettings()

// Send test message
JarvisDebug.sendMessage("Hello")

// Update provider
JarvisDebug.updateProvider('gemini', 'active')

// Clear chat
JarvisDebug.clearChat()

// Access logger
JarvisDebug.logger.info('msg')
JarvisDebug.logger.success('msg')
JarvisDebug.logger.error('msg')
```

## Customization

### Change Colors
Edit in `styles.css`:
```css
:root {
    --color-primary: #3b82f6;      /* Main blue */
    --color-secondary: #8b5cf6;    /* Purple */
    --color-accent: #ec4899;       /* Pink */
    --color-success: #10b981;      /* Green */
    --color-warning: #f59e0b;      /* Orange */
    --color-error: #ef4444;        /* Red */
}
```

### Change API Endpoint
Edit in `script.js`:
```javascript
const CONFIG = {
    API_BASE_URL: '/api',
    CHAT_ENDPOINT: '/chat',
};
```

### Enable/Disable Features
```javascript
// Sound notifications
State.settings.soundEnabled = false;

// Auto-scroll
State.settings.autoScroll = false;

// Timestamps
State.settings.showTimestamps = true;
```

## Network Requests

All requests are logged to console:

```
[INFO] Sending message to backend "Hello"
[SUCCESS] Response received {response: "Hi there!", provider: "gemini"}
```

Check Network tab in DevTools for:
- POST /api/chat - Message requests
- GET /css/styles.css - Stylesheet
- GET /js/script.js - JavaScript

## Responsive Breakpoints

```css
1024px+   → Desktop (sidebar fixed 320px)
768-1024px → Tablet (sidebar fixed 280px)
<768px    → Mobile (sidebar hidden)
<480px    → Small phone (compact mode)
```

## Voice Input Support

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome | ✅ | Full support |
| Edge | ✅ | Full support |
| Safari | ✅ | Limited iOS 14.5+ |
| Firefox | ❌ | No Web Speech API |

Use Chrome for best voice experience.

## Performance Tips

1. **Disable sounds** for better performance
   - Settings ⚙️ → Turn off notification sounds

2. **Disable auto-scroll** on slower devices
   - Settings ⚙️ → Turn off auto-scroll

3. **Browser DevTools**
   - F12 → Network → Throttle connection
   - F12 → Performance → Record interactions

## Troubleshooting

### Messages Not Sending
- Check backend is running
- Look for [ERROR] in console
- Verify API endpoint in CONFIG

### Voice Not Working
- Use Chrome, Edge, or Safari
- Check microphone permissions
- Look for "Speech Recognition Error" in console

### CSS Not Applying
- Check file path is correct
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+Shift+R)

### High Latency
- Check network connection
- Verify backend response time
- Look for slow API endpoint

## File Size Reference

- HTML: ~6 KB
- CSS: ~42 KB
- JavaScript: ~28 KB
- **Total: ~76 KB** (uncompressed)

With gzip compression: ~18 KB

## Cache Busting

To force users to get latest files, add version:

```html
<link rel="stylesheet" href="../app/static/css/styles.css?v=2.0" />
<script src="../app/static/js/script.js?v=2.0"></script>
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Send message |
| Shift+Enter | New line (if implemented) |
| Escape | Close settings modal |
| Tab | Navigate elements |

## Accessibility

- Semantic HTML
- ARIA labels on buttons
- Focus states on all interactive elements
- Color contrast WCAG AA compliant
- Keyboard navigation support

## Production Deployment

1. Minify CSS and JavaScript
2. Enable gzip compression
3. Set cache headers
4. Use CDN for static assets
5. Enable HTTPS
6. Monitor console errors
7. Test on target devices

## Support Resources

- Main docs: FRONTEND_GUIDE.md
- Quick start: QUICKSTART.md
- Deployment: DEPLOYMENT_GUIDE.md

---

**Version:** 2.0
**Status:** Production Ready ✅
**Last Updated:** Feb 21, 2026
