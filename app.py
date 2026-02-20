import os
import sys
import time
from flask import Flask, render_template, jsonify, request

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from app.services import provider_manager
from voice.speech_to_text import listen_voice

app = Flask(__name__, static_folder='static', template_folder='templates')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/query', methods=['POST'])
def api_query():
    try:
        data = request.get_json(force=True)
        prompt = data.get('prompt', '')
        start = time.time()
        result = provider_manager.query_with_fallback(prompt, max_tokens=int(data.get('max_tokens', 400)))
        latency = round(time.time() - start, 3)
        response_text = result.get('response') if result.get('status') == 'success' else ''
        return jsonify({
            'status': 'success',
            'user_input': prompt,
            'response': response_text,
            'provider': result.get('provider'),
            'latency': latency,
            'timestamp': time.time(),
            'raw': result
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/listen', methods=['GET'])
def api_listen():
    try:
        text = listen_voice()
        return jsonify({'status': 'success', 'text': text})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/speak', methods=['POST'])
def api_speak():
    try:
        data = request.get_json(force=True)
        text = data.get('text', '')
        # For compatibility keep server-side speak but prefer client TTS
        try:
            from voice.text_to_speech import speak
            speak(text)
        except Exception:
            pass
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)