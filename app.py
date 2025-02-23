from flask import Flask, request, jsonify, render_template
import requests
import os
from elevenlabs import text_to_speech, save
import traceback  # Import to log full errors


from dotenv import load_dotenv


# Load API keys from .env file (only for local use)
load_dotenv()

# Use API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

app = Flask(__name__)

# ElevenLabs API Key (keep this safe)


# OpenAI API URL (No need to import OpenAI module)
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/explain', methods=['POST'])
def explain_code():
    """Handles user requests for code explanation using OpenAI API via direct URL."""
    data = request.json
    code_snippet = data.get('code', '')
    language = data.get('language', 'English')

    if not code_snippet:
        return jsonify({'error': 'No code provided'}), 400

    prompt = f"Explain the following Python code in {language}:\n\n{code_snippet}"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
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
        print("Sending request to OpenAI...")
        response = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
        print("Response received from OpenAI.")

        response_json = response.json()
        print("OpenAI Response:", response_json)  # Debugging output

        if "choices" in response_json:
            explanation = response_json["choices"][0]["message"]["content"].strip()
            return jsonify({'explanation': explanation})
        else:
            return jsonify({'error': response_json.get("error", "Unknown error occurred")})

    except Exception as e:
        print(f"Error communicating with OpenAI: {str(e)}")  # Debugging output
        return jsonify({'error': str(e)}), 500


@app.route('/speak', methods=['POST'])
def speak_explanation():
    """Converts the AI-generated explanation into speech using ElevenLabs API."""
    data = request.json
    text = data.get('text', '').strip()
    language = data.get('language', 'English')  # Default to English if not provided


    if not text:
        print("❌ ERROR: No text provided")
        return jsonify({'error': 'No text provided'}), 400

    if not ELEVENLABS_API_KEY:
        print("❌ ERROR: ElevenLabs API key is missing")
        return jsonify({'error': 'ElevenLabs API key is missing'}), 400

    ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB"  # Replace with your actual voice ID

    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8
        }
    }

    try:
        print(f"🔄 Sending request to ElevenLabs API with language: {language}")

        response = requests.post(ELEVENLABS_API_URL, json=payload, headers=headers)

        print(f"🔄 ElevenLabs API responded with status: {response.status_code}")
        print(f"🔄 ElevenLabs API response body: {response.text}")

        if response.status_code == 200:
            audio_path = "static/explanation.mp3"
            print("✅ Saving audio file...")

            with open(audio_path, "wb") as audio_file:
                audio_file.write(response.content)

            return jsonify({'audio_url': '/' + audio_path})
        else:
            print(f"❌ ElevenLabs API Error: {response.text}")
            return jsonify({'error': f"ElevenLabs API error: {response.text}"}), 500

    except Exception as e:
        print("❌ Flask Server Error:", str(e))
        traceback.print_exc()  # This will print the full error traceback
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')  # Create 'static' folder if it doesn't exist
    app.run(debug=True)
