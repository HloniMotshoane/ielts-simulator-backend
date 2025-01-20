IELTS Speaking Simulator Backend
This backend service provides audio transcription and AI-powered follow-up question generation for an IELTS Speaking Simulator using AssemblyAI and Google Gemini.

Features
Transcribe audio files into text using AssemblyAI.
Generate contextually relevant follow-up questions based on user responses using Google Gemini.
Setup
Clone the repository:

bash
Copy
Edit
git clone https://github.com/HloniMotshoane/ielts-simulator-backend.git
cd ielts-simulator-backend
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Set the following environment variables in your terminal or .env file:

plaintext
Copy
Edit
GEMINI_API_KEY=your-gemini-api-key
ASSEMBLY_AI_API_KEY=your-assemblyai-api-key
Routes
POST /transcribe
Description: Transcribe audio files to text.
Request: Audio file (audio).
Response: Transcribed text.
POST /follow_up
Description: Generate a follow-up question based on user input text.
Request: JSON with text (user's response).
Response: JSON with the generated follow-up question and conversation history.
Running the App
bash
Copy
Edit
python app.py
The app will run on http://localhost:5001.

Dependencies
Flask
flask-cors
assemblyai
google-generativeai# ielts-simulator-backend
