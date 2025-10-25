🧠🎙️ AI Voice Assistant — Powered by LiveKit + Django + Streamlit
🚀 Real-time Voice Conversation Between Customers, AI Agents & Supervisors

An intelligent AI Voice Assistant that lets customers talk directly with an AI agent using their voice, powered by LiveKit for low-latency audio streaming and Django for backend intelligence.
When the AI cannot answer a query, it escalates automatically to a supervisor, and once the supervisor responds, the AI follows up instantly — maintaining a natural human-like conversation.

🌟 Key Features

🎤 Real-time Voice Chat with speech-to-text and text-to-speech

🧠 AI Response Engine with knowledge base matching (Trigram & difflib)

🧍‍💼 Supervisor Escalation System — when AI can’t answer

🔁 Automatic Follow-up when supervisor replies back

🎛️ LiveKit Integration for browser-based voice streaming

💬 Beautiful UI — black background with a white conversation box

🗃️ Django REST Backend with PostgreSQL

⚡ Streamlit Frontend for a fast, interactive interface

🧩 Tech Stack
Layer	Technologies Used
🎧 Voice Engine	LiveKit Cloud (WebRTC)
🧠 Backend	Django REST Framework, PostgreSQL
🖥️ Frontend	Streamlit (HTML + JS custom components)
🧩 AI Matching	TrigramSimilarity + difflib
🗣️ Speech Processing	Web Speech API (Recognition + Synthesis)
☁️ Hosting Ready	Compatible with Render, Railway, or LiveKit Cloud
🏗️ Project Architecture
Customer (Voice)
   ↓
Browser (Streamlit + LiveKit)
   ↓
Speech Recognition (Web Speech API)
   ↓
Django Backend (/api/chat/)
   ↓
Knowledge Base → AI Responds if matched
   ↓
If no match → Escalate to Supervisor (/api/chat/followup/)
   ↓
Supervisor responds → AI follows up automatically
   ↓
Speech Synthesis (AI speaks back)

⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/<your-username>/ai-voice-assistant.git
cd ai-voice-assistant

2️⃣ Backend Setup (Django)
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver


Create a .env file inside the backend directory:

LIVEKIT_URL=wss://your-livekit-domain.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret

3️⃣ Frontend Setup (Streamlit)
cd streamlit_app
streamlit run voice_chat.py

💬 Usage Demo

Click 🎤 Start Talking on the Streamlit UI.

Ask a question like:

“What are your salon working hours?”
The AI listens and answers instantly.

Ask something not in the knowledge base:

“Do you accept UPI payments?”
The AI escalates to a supervisor:
“Please wait, let me connect with supervisor…”

When the supervisor replies in their panel, the AI follows up automatically:

“My supervisor says: yes, we do.”
🧠 Core Files
File	Description
voice_chat.py	Streamlit frontend for voice chat
api_views.py	Django API for chat, follow-up, and token generation
models.py	Database models for AI, Supervisor, and Requests
urls.py	Backend routing for APIs
requirements.txt	Python dependencies
