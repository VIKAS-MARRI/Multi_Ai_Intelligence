/**
 * Jarvis Multi-AI Voice Assistant
 * Main Frontend Application Logic
 * Enterprise-grade client-side implementation
 */

class JarvisAssistant {
    constructor() {
        this.isListening = false;
        this.isLoading = false;
        this.apiBaseUrl = '/api';
        this.initializeElements();
        this.attachEventListeners();
        this.loadConfiguration();
    }

    /**
     * Initialize DOM elements for easy access
     */
    initializeElements() {
        // Input elements
        this.promptInput = document.getElementById('promptInput');
        this.voiceInputBtn = document.getElementById('voiceInputBtn');
        this.queryBtn = document.getElementById('queryBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.fusionToggle = document.getElementById('fusionToggle');

        // Status elements
        this.statusIndicator = document.getElementById('statusIndicator');
        this.statusText = document.getElementById('statusText');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        this.loadingText = document.getElementById('loadingText');

        // Response containers
        this.responsesContainer = document.getElementById('responsesContainer');
        this.fusedResponseCard = document.getElementById('fusedResponseCard');
        this.fusedContent = document.getElementById('fusedContent');
        this.fusedConfidence = document.getElementById('fusedConfidence');
        this.playFusedBtn = document.getElementById('playFusedBtn');

        // Individual response elements
        this.responses = {
            openai: {
                card: document.getElementById('openaiCard'),
                content: document.getElementById('openaiContent'),
                status: document.getElementById('openaiStatus'),
                statusText: document.getElementById('openaiStatusText')
            },
            gemini: {
                card: document.getElementById('geminiCard'),
                content: document.getElementById('geminiContent'),
                status: document.getElementById('geminiStatus'),
                statusText: document.getElementById('geminiStatusText')
            },
            deepseek: {
                card: document.getElementById('deepseekCard'),
                content: document.getElementById('deepseekContent'),
                status: document.getElementById('deepseekStatus'),
                statusText: document.getElementById('deepseekStatusText')
            }
        };

        // Audio element
        this.audioOutput = document.getElementById('audioOutput');
    }

    /**
     * Attach event listeners to UI elements
     */
    attachEventListeners() {
        this.queryBtn.addEventListener('click', () => this.handleQuery());
        this.clearBtn.addEventListener('click', () => this.handleClear());
        this.voiceInputBtn.addEventListener('click', () => this.handleVoiceInput());
        this.playFusedBtn.addEventListener('click', () => this.playFusedResponse());
        this.promptInput.addEventListener('keypress', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.handleQuery();
            }
        });

        // Prevent form submission
        document.addEventListener('submit', (e) => e.preventDefault());
    }

    /**
     * Load configuration from server
     */
    async loadConfiguration() {
        try {
            const response = await fetch('/api/config');
            const config = await response.json();
            console.log('Configuration loaded:', config);
        } catch (error) {
            console.error('Failed to load configuration:', error);
        }
    }

    /**
     * Update status indicator
     */
    updateStatus(status, message, indicator = 'info') {
        const colors = {
            info: 'bg-blue-500',
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500',
            loading: 'bg-blue-500 animate-pulse'
        };

        this.statusIndicator.className = `w-2 h-2 rounded-full ${colors[indicator]}`;
        this.statusText.textContent = message;
    }

    /**
     * Show loading state
     */
    showLoading(message = 'Querying AI models...') {
        this.isLoading = true;
        this.loadingSpinner.classList.remove('hidden');
        this.loadingText.textContent = message;
        this.queryBtn.disabled = true;
        this.voiceInputBtn.disabled = true;
        this.updateStatus('loading', 'Processing...', 'loading');

        // Reset response displays
        Object.values(this.responses).forEach(resp => {
            resp.card.classList.add('hidden');
        });
        this.fusedResponseCard.classList.add('hidden');
    }

    /**
     * Hide loading state
     */
    hideLoading() {
        this.isLoading = false;
        this.loadingSpinner.classList.add('hidden');
        this.queryBtn.disabled = false;
        this.voiceInputBtn.disabled = false;
    }

    /**
     * Display individual AI responses
     */
    displayResponses(data) {
        const { openai, gemini, deepseek } = data.responses;

        // Display individual responses
        this.displayResponse(openai, 'openai');
        this.displayResponse(gemini, 'gemini');
        this.displayResponse(deepseek, 'deepseek');
    }

    /**
     * Display individual response in card
     */
    displayResponse(response, provider) {
        const resp = this.responses[provider];

        if (response.status === 'success') {
            resp.content.textContent = response.response || 'No response received';
            resp.status.className = 'w-2 h-2 bg-green-500 rounded-full inline-block';
            resp.statusText.textContent = ' Success';
            resp.card.classList.remove('hidden');
        } else {
            resp.content.textContent = response.message || 'Error occurred';
            resp.status.className = 'w-2 h-2 bg-red-500 rounded-full inline-block';
            resp.statusText.textContent = ' Error';
            resp.card.classList.remove('hidden');
        }

        // Add animation
        resp.card.classList.add('slide-up');
    }

    /**
     * Display fused response
     */
    displayFusedResponse(fusedData) {
        if (fusedData.status === 'success') {
            this.fusedContent.textContent = fusedData.fused_response || 'Error generating fused response';
            this.fusedConfidence.textContent = `Confidence: ${(fusedData.confidence * 100).toFixed(0)}% | Providers: ${fusedData.num_providers}`;
            this.fusedResponseCard.classList.remove('hidden');
            this.fusedResponseCard.classList.add('slide-up');
        } else {
            console.error('Fusion error:', fusedData.message);
        }
    }

    /**
     * Handle main query submission
     */
    async handleQuery() {
        const prompt = this.promptInput.value.trim();

        if (!prompt) {
            this.updateStatus('error', 'Please enter a question', 'warning');
            return;
        }

        this.showLoading();

        try {
            this.updateStatus('loading', 'Sending query...', 'loading');

            const response = await fetch(`${this.apiBaseUrl}/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: prompt,
                    max_tokens: 1000,
                    enable_fusion: this.fusionToggle.checked
                })
            });

            // Protect against non-JSON error pages (HTML stacktraces)
            const contentType = response.headers.get('content-type') || '';
            if (!response.ok) {
                if (contentType.includes('application/json')) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || 'Failed to process query');
                } else {
                    const text = await response.text();
                    throw new Error(text.slice(0, 1000) || 'Failed to process query (non-JSON response)');
                }
            }

            if (!contentType.includes('application/json')) {
                const text = await response.text();
                throw new Error('Server returned non-JSON response: ' + text.slice(0, 1000));
            }

            const data = await response.json();

            if (data.status === 'success') {
                // Display individual responses
                this.displayResponses(data);

                // Display fused response if enabled and available
                if (this.fusionToggle.checked && data.fused_response) {
                    this.displayFusedResponse(data.fused_response);
                }

                this.updateStatus('success', 'Response received', 'success');

                // Auto-play fused response if enabled
                if (this.fusionToggle.checked && data.fused_response?.status === 'success') {
                    setTimeout(() => this.playFusedResponse(), 500);
                }
            } else {
                throw new Error(data.message || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('Query error:', error);
            this.updateStatus('error', `Error: ${error.message}`, 'error');
            this.showErrorMessage(error.message);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Handle voice input
     */
    async handleVoiceInput() {
        if (this.isListening) {
            this.updateStatus('error', 'Voice input is not available in browser', 'error');
            return;
        }

        this.isListening = true;
        this.voiceInputBtn.disabled = true;
        this.updateStatus('loading', 'Listening...', 'loading');

        try {
            // Browser's native Speech Recognition API
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

            if (!SpeechRecognition) {
                throw new Error('Speech Recognition not supported in your browser');
            }

            const recognition = new SpeechRecognition();
            recognition.lang = 'en-US';
            recognition.continuous = false;
            recognition.interimResults = true;

            recognition.onstart = () => {
                this.updateStatus('loading', 'Recording...', 'loading');
            };

            recognition.onresult = (event) => {
                let transcript = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    transcript += event.results[i][0].transcript;
                }
                this.promptInput.value = transcript;
            };

            recognition.onerror = (event) => {
                this.updateStatus('error', `Voice input error: ${event.error}`, 'error');
            };

            recognition.onend = () => {
                this.isListening = false;
                this.voiceInputBtn.disabled = false;
                if (this.promptInput.value.trim()) {
                    this.handleQuery();
                }
            };

            recognition.start();
        } catch (error) {
            console.error('Voice input error:', error);
            this.updateStatus('error', error.message, 'error');
            this.isListening = false;
            this.voiceInputBtn.disabled = false;
        }
    }

    /**
     * Play fused response as audio
     */
    async playFusedResponse() {
        const text = this.fusedContent.textContent.trim();

        if (!text) {
            this.updateStatus('error', 'No text to speak', 'warning');
            return;
        }

        this.playFusedBtn.disabled = true;

        try {
            this.updateStatus('loading', 'Generating speech...', 'loading');

            const response = await fetch(`${this.apiBaseUrl}/text-to-speech`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text
                })
            });

            if (!response.ok) {
                throw new Error('Failed to generate speech');
            }

            const data = await response.json();

            if (data.status === 'success') {
                this.audioOutput.src = data.audio_url;
                this.audioOutput.play();
                this.updateStatus('success', 'Playing response', 'success');
            } else {
                throw new Error(data.message || 'Failed to generate speech');
            }
        } catch (error) {
            console.error('Text-to-speech error:', error);
            this.updateStatus('error', `Audio error: ${error.message}`, 'error');
        } finally {
            this.playFusedBtn.disabled = false;
        }
    }

    /**
     * Handle clear button
     */
    handleClear() {
        this.promptInput.value = '';
        this.responsesContainer.innerHTML = '';
        this.updateStatus('info', 'Ready', 'info');
        this.promptInput.focus();

        // Reset response cards
        Object.values(this.responses).forEach(resp => {
            resp.card.classList.add('hidden');
            resp.content.textContent = '';
        });
        this.fusedResponseCard.classList.add('hidden');
        this.fusedContent.textContent = '';
    }

    /**
     * Show error message
     */
    showErrorMessage(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        this.responsesContainer.insertBefore(errorDiv, this.responsesContainer.firstChild);

        setTimeout(() => errorDiv.remove(), 5000);
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.jarvis = new JarvisAssistant();
    console.log('Jarvis Multi-AI Assistant initialized');
});

// Handle visibility change for state management
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('Application hidden');
    } else {
        console.log('Application visible');
    }
});

// Handle before unload
window.addEventListener('beforeunload', (e) => {
    if (window.jarvis && window.jarvis.isLoading) {
        e.preventDefault();
        e.returnValue = '';
    }
});
