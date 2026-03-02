/**
 * Jarvis Enterprise Assistant - Main Script
 * Modern UI with chat functionality, provider management, and voice support
 * © 2026 - Production Ready
 */

console.log('%c🚀 Jarvis Assistant initialized', 'color: #3b82f6; font-weight: bold; font-size: 14px;');

// ========================================
// Configuration
// ========================================

const CONFIG = {
    API_BASE_URL: '/api',
    CHAT_ENDPOINT: '/chat',
    AUTO_SCROLL: true,
    SOUND_ENABLED: true,
    SHOW_TIMESTAMPS: false,
    MESSAGE_ANIMATION_DURATION: 300,
    TYPING_ANIMATION_DURATION: 1400,
};

// ========================================
// Application State
// ========================================

const State = {
    isLoading: false,
    isSending: false,
    messageCount: 0,
    conversationHistory: [],
    providers: {
        gemini: { status: 'idle', icon: '🔮' },
        openai: { status: 'idle', icon: '🤖' },
        deepseek: { status: 'idle', icon: '🎯' },
        fallback: { status: 'active', icon: '🔄' },
    },
    settings: {
        autoScroll: true,
        soundEnabled: true,
        showTimestamps: false,
    },
};

// ========================================
// DOM Elements
// ========================================

const DOM = {
    // Sidebar
    sidebar: document.querySelector('.sidebar'),
    settingsBtn: document.getElementById('settings-btn'),

    // Chat area
    messagesArea: document.getElementById('messages-area'),
    chatContainer: document.querySelector('.chat-container'),
    typingIndicator: document.getElementById('typing-indicator'),

    // Input controls
    messageInput: document.getElementById('message-input'),
    sendButton: document.getElementById('send-button'),
    micButton: document.getElementById('mic-button'),
    clearChatBtn: document.getElementById('clear-chat-btn'),

    // Modal
    modal: document.getElementById('settings-modal'),
    modalClose: document.getElementById('modal-close'),

    // Settings
    autoScrollToggle: document.getElementById('auto-scroll-toggle'),
    soundToggle: document.getElementById('sound-toggle'),
    timestampToggle: document.getElementById('timestamp-toggle'),

    // Provider cards
    providers: {
        gemini: document.getElementById('provider-gemini'),
        openai: document.getElementById('provider-openai'),
        deepseek: document.getElementById('provider-deepseek'),
        fallback: document.getElementById('provider-fallback'),
    },
};

// ========================================
// Utility Functions
// ========================================

/**
 * Log helper with consistent styling
 */
const logger = {
    info: (msg, data = null) => {
        console.log(`%c[INFO] ${msg}`, 'color: #3b82f6; font-weight: bold;', data || '');
    },
    success: (msg, data = null) => {
        console.log(`%c[SUCCESS] ${msg}`, 'color: #10b981; font-weight: bold;', data || '');
    },
    error: (msg, data = null) => {
        console.error(`%c[ERROR] ${msg}`, 'color: #ef4444; font-weight: bold;', data || '');
    },
    warn: (msg, data = null) => {
        console.warn(`%c[WARN] ${msg}`, 'color: #f59e0b; font-weight: bold;', data || '');
    },
};

/**
 * Get current timestamp
 */
const getTimestamp = () => {
    const now = new Date();
    return now.toLocaleTimeString(undefined, {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
    });
};

/**
 * Scroll to bottom of messages
 */
const scrollToBottom = () => {
    if (!State.settings.autoScroll) return;

    setTimeout(() => {
        DOM.messagesArea.scrollTop = DOM.messagesArea.scrollHeight;
    }, 50);
};

/**
 * Play notification sound
 */
const playSound = (type = 'message') => {
    if (!State.settings.soundEnabled) return;

    // Create a simple beep using Web Audio API
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        const now = audioContext.currentTime;

        if (type === 'message') {
            oscillator.frequency.value = 523.25; // C5
            gainNode.gain.setValueAtTime(0.1, now);
            gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.1);

            oscillator.start(now);
            oscillator.stop(now + 0.1);
        } else if (type === 'send') {
            oscillator.frequency.value = 783.99; // G5
            gainNode.gain.setValueAtTime(0.1, now);
            gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.08);

            oscillator.start(now);
            oscillator.stop(now + 0.08);
        }
    } catch (error) {
        logger.warn('Audio API not available', error);
    }
};

/**
 * Escape HTML to prevent XSS
 */
const escapeHtml = (text) => {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
};

// ========================================
// Message Management
// ========================================

/**
 * Create and display user message
 */
const createUserMessage = (text) => {
    logger.info('Creating user message', text);

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.innerHTML = `
        <div class="message-content">${escapeHtml(text)}</div>
    `;

    DOM.messagesArea.appendChild(messageDiv);
    State.messageCount++;
    scrollToBottom();
    playSound('send');
};

/**
 * Create and display assistant message
 */
const createAssistantMessage = (text) => {
    logger.info('Creating assistant message');

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';

    // Append before showing typing indicator
    DOM.messagesArea.appendChild(messageDiv);

    // Simulate typing animation
    let displayText = '';
    let charIndex = 0;
    const typingSpeed = 10; // ms per character

    const typeOut = () => {
        if (charIndex < text.length) {
            displayText += text[charIndex];
            messageDiv.innerHTML = `<div class="message-content">${escapeHtml(displayText)}</div>`;
            charIndex++;

            scrollToBottom();
            setTimeout(typeOut, typingSpeed);
        } else {
            logger.success('Message complete');
            playSound('message');
        }
    };

    typeOut();
    State.messageCount++;
};

/**
 * Show typing indicator
 */
const showTypingIndicator = () => {
    logger.info('Showing typing indicator');
    DOM.typingIndicator.classList.add('active');
    scrollToBottom();
};

/**
 * Hide typing indicator
 */
const hideTypingIndicator = () => {
    logger.info('Hiding typing indicator');
    DOM.typingIndicator.classList.remove('active');
};

// ========================================
// Provider Management
// ========================================

/**
 * Update provider status in UI
 */
const updateProviderStatus = (provider, status) => {
    logger.info(`Updating ${provider} status to ${status}`);

    State.providers[provider].status = status;
    const providerCard = DOM.providers[provider];

    if (!providerCard) {
        logger.warn(`Provider card for ${provider} not found`);
        return;
    }

    const statusIndicator = providerCard.querySelector('.status-indicator');
    const statusText = providerCard.querySelector('.status-text');

    // Remove old status classes
    statusIndicator.classList.remove('active', 'idle', 'error');

    // Add new status class
    if (status === 'active') {
        statusIndicator.classList.add('active');
        statusText.textContent = 'Active';
    } else if (status === 'error') {
        statusIndicator.classList.add('error');
        statusText.textContent = 'Error';
    } else {
        statusIndicator.classList.add('idle');
        statusText.textContent = 'Idle';
    }
};

// ========================================
// Chat Functionality
// ========================================

/**
 * Send message to backend
 */
const sendMessage = async (text) => {
    if (!text.trim()) {
        logger.warn('Empty message attempted');
        return;
    }

    if (State.isSending || State.isLoading) {
        logger.warn('Send operation already in progress');
        return;
    }

    try {
        State.isSending = true;
        logger.info('Sending message to backend', text);

        // Show user message immediately
        createUserMessage(text);
        DOM.messageInput.value = '';

        // Show typing indicator
        showTypingIndicator();

        // Simulate provider status change
        updateProviderStatus('fallback', 'active');

        // Send request to backend
        const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.CHAT_ENDPOINT}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: text,
                conversation_id: 'web-session',
                provider: 'auto', // Let backend choose
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        logger.success('Response received', data);

        hideTypingIndicator();

        // Extract response text
        const responseText = data.response || data.content || 'No response received';
        const provider = data.provider || 'fallback';

        // Update provider status
        if (provider === 'gemini') updateProviderStatus('gemini', 'active');
        else if (provider === 'openai') updateProviderStatus('openai', 'active');
        else if (provider === 'deepseek') updateProviderStatus('deepseek', 'active');
        else updateProviderStatus('fallback', 'active');

        // Display response with typing animation
        createAssistantMessage(responseText);

        // Store in conversation history
        State.conversationHistory.push({
            role: 'user',
            content: text,
        });
        State.conversationHistory.push({
            role: 'assistant',
            content: responseText,
            provider: provider,
        });
    } catch (error) {
        logger.error('Error sending message', error);
        hideTypingIndicator();

        // Show error message
        const errorMsg = `⚠️ Error: ${error.message}. Please try again or check your connection.`;
        createAssistantMessage(errorMsg);

        // Update provider status to error
        updateProviderStatus('fallback', 'error');
    } finally {
        State.isSending = false;
        DOM.messageInput.focus();
    }
};

// ========================================
// Event Listeners
// ========================================

/**
 * Send button click
 */
DOM.sendButton.addEventListener('click', () => {
    logger.info('Send button clicked');
    const message = DOM.messageInput.value.trim();
    if (message) {
        sendMessage(message);
    }
});

/**
 * Message input - Enter key
 */
DOM.messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        logger.info('Enter key pressed');
        const message = DOM.messageInput.value.trim();
        if (message) {
            sendMessage(message);
        }
    }
});

/**
 * Microphone button click
 */
DOM.micButton.addEventListener('click', () => {
    logger.info('Microphone button clicked');

    // Check for Web Speech API
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        logger.error('Speech Recognition API not available');
        alert('Speech Recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
        return;
    }

    // Toggle listening state
    const isListening = DOM.micButton.classList.toggle('listening');

    if (isListening) {
        logger.info('Starting speech recognition');

        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            logger.info('Speech recognition started');
            DOM.messageInput.placeholder = '🎤 Listening...';
        };

        recognition.onresult = (event) => {
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;

                if (event.results[i].isFinal) {
                    logger.info('Final transcript', transcript);
                    DOM.messageInput.value = transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            if (interimTranscript) {
                DOM.messageInput.placeholder = `🎤 Heard: "${interimTranscript}"...`;
            }
        };

        recognition.onerror = (event) => {
            logger.error('Speech recognition error', event.error);
            DOM.micButton.classList.remove('listening');
            DOM.messageInput.placeholder = 'Type a message or click the microphone...';
        };

        recognition.onend = () => {
            logger.info('Speech recognition ended');
            DOM.micButton.classList.remove('listening');
            DOM.messageInput.placeholder = 'Type a message or click the microphone...';

            // Auto-send if there's text
            const message = DOM.messageInput.value.trim();
            if (message) {
                sendMessage(message);
            }
        };

        recognition.start();
    }
});

/**
 * Clear chat button
 */
DOM.clearChatBtn.addEventListener('click', () => {
    logger.info('Clear chat requested');

    if (confirm('Are you sure you want to clear all messages?')) {
        DOM.messagesArea.innerHTML = `
            <div class="system-message">
                <div class="system-content">
                    <h2>Welcome to Jarvis</h2>
                    <p>Your enterprise voice assistant powered by multiple AI models</p>
                    <p class="system-hint">💡 Try asking me anything - I can use Gemini, OpenAI, DeepSeek, or fallback models</p>
                </div>
            </div>
        `;
        State.messageCount = 0;
        State.conversationHistory = [];
        logger.success('Chat cleared');
    }
});

/**
 * Settings button
 */
DOM.settingsBtn.addEventListener('click', () => {
    logger.info('Settings opened');
    DOM.modal.classList.add('active');
});

/**
 * Modal close button
 */
DOM.modalClose.addEventListener('click', () => {
    logger.info('Settings closed');
    DOM.modal.classList.remove('active');
});

/**
 * Modal backdrop click
 */
DOM.modal.addEventListener('click', (e) => {
    if (e.target === DOM.modal) {
        logger.info('Modal closed via backdrop');
        DOM.modal.classList.remove('active');
    }
});

/**
 * Settings - Auto scroll toggle
 */
DOM.autoScrollToggle.addEventListener('change', (e) => {
    State.settings.autoScroll = e.target.checked;
    logger.info('Auto scroll toggled', State.settings.autoScroll);
    localStorage.setItem('jarvis-auto-scroll', State.settings.autoScroll);
});

/**
 * Settings - Sound toggle
 */
DOM.soundToggle.addEventListener('change', (e) => {
    State.settings.soundEnabled = e.target.checked;
    logger.info('Sound toggled', State.settings.soundEnabled);
    localStorage.setItem('jarvis-sound', State.settings.soundEnabled);
});

/**
 * Settings - Timestamp toggle
 */
DOM.timestampToggle.addEventListener('change', (e) => {
    State.settings.showTimestamps = e.target.checked;
    logger.info('Timestamps toggled', State.settings.showTimestamps);
    localStorage.setItem('jarvis-timestamps', State.settings.showTimestamps);
});

/**
 * Focus message input on load
 */
DOM.messageInput.addEventListener('load', () => {
    DOM.messageInput.focus();
});

// ========================================
// Initialization
// ========================================

/**
 * Load settings from localStorage
 */
const loadSettings = () => {
    logger.info('Loading settings from localStorage');

    const autoScroll = localStorage.getItem('jarvis-auto-scroll');
    const soundEnabled = localStorage.getItem('jarvis-sound');
    const showTimestamps = localStorage.getItem('jarvis-timestamps');

    if (autoScroll !== null) {
        State.settings.autoScroll = autoScroll === 'true';
        DOM.autoScrollToggle.checked = State.settings.autoScroll;
    }

    if (soundEnabled !== null) {
        State.settings.soundEnabled = soundEnabled === 'true';
        DOM.soundToggle.checked = State.settings.soundEnabled;
    }

    if (showTimestamps !== null) {
        State.settings.showTimestamps = showTimestamps === 'true';
        DOM.timestampToggle.checked = State.settings.showTimestamps;
    }

    logger.success('Settings loaded', State.settings);
};

/**
 * Verify all DOM elements are loaded
 */
const verifyDOM = () => {
    logger.info('🔍 Verifying DOM elements...');

    const elements = {
        'messagesArea': DOM.messagesArea,
        'messageInput': DOM.messageInput,
        'sendButton': DOM.sendButton,
        'micButton': DOM.micButton,
        'typingIndicator': DOM.typingIndicator,
        'modal': DOM.modal,
    };

    let allPresent = true;

    for (const [name, element] of Object.entries(elements)) {
        if (!element) {
            logger.error(`Missing DOM element: ${name}`);
            allPresent = false;
        } else {
            logger.success(`✓ Found: ${name}`);
        }
    }

    return allPresent;
};

/**
 * Verify CSS file is loaded
 */
const verifyCSSLoaded = () => {
    logger.info('🔍 Verifying CSS loaded...');

    const styles = window.getComputedStyle(document.body);
    const bgColor = styles.backgroundColor;

    if (bgColor) {
        logger.success(`✓ CSS loaded - Body background: ${bgColor}`);
        return true;
    } else {
        logger.warn('CSS may not be fully loaded');
        return false;
    }
};

/**
 * Initialize application
 */
const initializeApp = () => {
    logger.info('========================================');
    logger.info('Initializing Jarvis Assistant Application');
    logger.info('========================================');

    // Verify DOM
    if (!verifyDOM()) {
        logger.error('Critical: Some DOM elements are missing!');
        return false;
    }

    // Verify CSS
    verifyCSSLoaded();

    // Load settings
    loadSettings();

    // Set initial focus
    DOM.messageInput.focus();

    // Log API endpoint
    logger.info('API Base URL:', CONFIG.API_BASE_URL);
    logger.info('Chat Endpoint:', CONFIG.CHAT_ENDPOINT);

    // Log provider status
    logger.info('Provider Status:', State.providers);

    logger.success('✅ Application initialized successfully!');
    logger.info('Type a message or click the microphone to start');

    return true;
};

/**
 * Initialize on DOM ready
 */
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// ========================================
// Global Error Handler
// ========================================

window.addEventListener('error', (event) => {
    logger.error('Uncaught error', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
    });
});

window.addEventListener('unhandledrejection', (event) => {
    logger.error('Unhandled promise rejection', event.reason);
});

// ========================================
// Export for debugging
// ========================================

window.JarvisDebug = {
    getState: () => State,
    getSettings: () => State.settings,
    sendMessage: (msg) => sendMessage(msg),
    updateProvider: (provider, status) => updateProviderStatus(provider, status),
    clearChat: () => {
        DOM.messagesArea.innerHTML = '';
        State.messageCount = 0;
    },
    logger: logger,
    CONFIG: CONFIG,
};

logger.info('Debug object available at window.JarvisDebug');
