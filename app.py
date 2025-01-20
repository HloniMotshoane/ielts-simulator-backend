from flask import Flask, request, jsonify
from flask_cors import CORS
import assemblyai as aai
import os
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Configuration
app.config.from_mapping(
    GEMINI_API_KEY=os.environ.get("GEMINI_API_KEY"),
    ASSEMBLY_AI_API_KEY=os.environ.get("ASSEMBLY_AI_API_KEY"),
)

# Set API keys
genai.configure(api_key=app.config["GEMINI_API_KEY"])
aai.settings.api_key = app.config["ASSEMBLY_AI_API_KEY"]

# Set up Gemini model for follow-up question generation
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
)

# Global variable to store conversation history
conversation_history = []

@app.route('/', methods=['POST'])
def home():
    print('Working')
    return jsonify({"message": "Server is working"})

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    print('Transcribing audio...')
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    print(f"Received file: {audio_file.filename}, size: {len(audio_file.read())} bytes")
    audio_file.seek(0)  # Reset file pointer

    try:
        # Transcribe using AssemblyAI
        transcriber = aai.Transcriber()
        config = aai.TranscriptionConfig(speaker_labels=True)
        transcript = transcriber.transcribe(audio_file, config)

        if transcript.status == aai.TranscriptStatus.error:
            print(f"Transcription error: {transcript.error}")
            return jsonify({"error": transcript.error}), 500

        print(f"Transcription success: {transcript.text}")
        return jsonify({"transcript": transcript.text})

    except Exception as e:
        print(f"Error in transcription: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/follow_up', methods=['POST'])
def follow_up():
    print("Generating follow-up question...")

    # Expecting the request body to contain JSON with "text"
    if not request.json or 'text' not in request.json:
        return jsonify({"error": "No text provided"}), 400

    user_response = request.json['text']
    
    # Define the topic for the conversation (could be dynamic based on input or logic)
    topic = "Travel"  # Modify as needed based on context

    try:
        # Initialize conversation history if it's the first interaction
        global conversation_history
        if 'conversation_history' not in globals():
            conversation_history = [
                {
                    "role": "system",
                    "parts": [
                        "You are an IELTS Speaking Examiner. Engage the user in a real-time speaking simulation. "
                        "Based on the user's responses, generate follow-up questions that are contextually relevant, "
                        "challenging, and conversational."
                    ],
                }
            ]

        # Add the user's current response to the history
        conversation_history.append({
            "role": "user",
            "parts": [user_response]
        })

        # Generate follow-up question using Gemini
        chat_session = model.start_chat(history=conversation_history)
        response = chat_session.send_message(
            f"Based on the user's response: \"{user_response}\", generate a single, concise follow-up question. "
            "The question should: \n"
            "1. Be contextually relevant to the user's input.\n"
            "2. Encourage the user to elaborate further on their thoughts.\n"
            "3. Be clear and conversational.\n\n"
            "Provide only the follow-up question, nothing else."
        )
        follow_up_question = response.text.strip()

        # Add the follow-up question to the conversation history
        conversation_history.append({
            "role": "model",
            "parts": [follow_up_question]
        })

        # Prepare and return the updated conversation
        conversation = {
            "topic": topic,
            "conversation_history": conversation_history
        }

        print(f"Updated conversation: {conversation}")
        return jsonify(conversation)

    except Exception as e:
        print(f"Error in generating follow-up question: {e}")
        return jsonify({"error": str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True, port=5001)