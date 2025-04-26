from flask import Flask, request, jsonify, send_file
import openai
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ElevenLabs API details
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")  # You need to set this in your .env file too

# Function to generate voice using ElevenLabs
def generate_voice(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "accept": "audio/mpeg",
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.7
        }
    }
    response = requests.post(url, json=data, headers=headers)

    # Save the audio output to a file
    with open("response.mp3", "wb") as f:
        f.write(response.content)

    return "response.mp3"

# Chatbot endpoint
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Send user message to OpenAI GPT model
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": """
You are Sanjana's AI twin.

Always talk warmly, naturally, and like a friendly human. Use expressions like "Hey!", "Sure thing!", "I'd love to tell you!" to make conversation lively and engaging.

Only discuss Sanjana’s career journey, skills, achievements, educational background, certifications, projects, work experience.

If someone asks anything outside of Sanjana's professional background, politely reply:
"Hey! I’m here just to talk about Sanjana’s amazing career and projects. Feel free to ask about that!"

Keep answers friendly, positive, and a little playful — but always stay professional when needed.

Sound casual but confident, like Sanjana would when talking about herself.
"""},
            {"role": "user", "content": user_message}
        ],
        max_tokens=400  # Longer and more complete replies
    )

    bot_reply = response.choices[0].message.content.strip()

    # Generate voice for the reply
    audio_file_path = generate_voice(bot_reply)

    return jsonify({
        'reply': bot_reply,
        'audio_url': '/get_audio'  # Endpoint to fetch the generated audio
    })

# Endpoint to serve the voice audio
@app.route('/get_audio', methods=['GET'])
def get_audio():
    return send_file("response.mp3", mimetype="audio/mpeg")

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
