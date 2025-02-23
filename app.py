from flask import Flask, request, jsonify, render_template
import requests
import os
from elevenlabs import text_to_speech, save
from APIKEY import apikey1
from APIKEY import apikey2


app = Flask(__name__)

# ElevenLabs API Key (keep this safe)
ELEVENLABS_API_KEY = apikey2

# OpenAI API URL (No need to import OpenAI module)
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = apikey1  # Better to store this in environment variables


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/explain', methods=['POST'])
def explain_code():
    """Handles user requests for code explanation using OpenAI API via direct URL."""
    data = request.json
    code_snippet = data.get('code', '')
    language = data.get('language', 'English')
    openai_key = data.get('openaiKey', '')

    if not code_snippet:
        return jsonify({'error': 'No code provided'}), 400
    if not openai_key:
        return jsonify({'error': 'Missing OpenAI API key'}), 400

    prompt = f"Explain the following Python code in {language}:\n\n{code_snippet}"

    headers = {
        "Authorization": f"Bearer {openai_key}",  # Use the user's API key
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are an AI assistant that explains code in simple terms."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 150,
        "temperature": 0.5
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
        response_json = response.json()

        if "choices" in response_json:
            explanation = response_json["choices"][0]["message"]["content"].strip()
            return jsonify({'explanation': explanation})
        else:
            return jsonify({'error': response_json.get("error", "Unknown error occurred")})

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/speak', methods=['POST'])
def speak_explanation():
    """Converts the AI-generated explanation into speech using ElevenLabs API."""
    data = request.json
    text = data.get('text', '')
    elevenlabs_key = data.get('elevenlabsKey', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400
    if not elevenlabs_key:
        return jsonify({'error': 'Missing ElevenLabs API key'}), 400

    ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB"

    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": elevenlabs_key,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8
        }
    }

    try:
        response = requests.post(ELEVENLABS_API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            audio_path = "static/explanation.mp3"

            with open(audio_path, "wb") as audio_file:
                audio_file.write(response.content)

            return jsonify({'audio_url': '/' + audio_path})
        else:
            return jsonify({'error': f"ElevenLabs API error: {response.text}"}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')  # Create 'static' folder if it doesn't exist
    app.run(debug=True)
