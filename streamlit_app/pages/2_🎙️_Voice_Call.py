import streamlit as st

DJANGO_CHAT_API = "http://127.0.0.1:8000/api/chat/"
DJANGO_FOLLOWUP_API = "http://127.0.0.1:8000/api/chat/followup/"

# --- UI styling ---
st.markdown("""
    <style>
        .stApp {
            background-color: white !important;
            color: black !important;
        }
        .block-container {
            padding-top: 5rem;
            text-align: center;
        }
        header, footer {
            background-color: white !important;
        }
        #conversation p {
            margin: 6px 0;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🧠🎙️ AI Voice Assistant")

st.components.v1.html(f"""
  <div style="text-align:center;">
    <button id="startRec"
            style="padding:12px 24px;font-size:16px;border-radius:8px;
                   background-color:#28a745;color:white;border:none;cursor:pointer;">
      🎤 Start Talking
    </button>
    <button id="stopRec"
            style="padding:12px 24px;font-size:16px;border-radius:8px;margin-left:10px;
                   background-color:#dc3545;color:white;border:none;cursor:pointer;display:none;">
      ⏹️ Stop
    </button>
    <p id="status" style="margin-top:10px;font-weight:500;"></p>
    
    <div id="conversation" style="margin-top:20px;text-align:left;width:70%;margin:auto;
                                  background:#f9f9f9;border-radius:10px;padding:15px;
                                  box-shadow:0 2px 6px rgba(0,0,0,0.1);max-height:400px;overflow-y:auto;">
      <p><b>🗣️ Conversation:</b></p>
    </div>
  </div>

  <script>
    const startBtn = document.getElementById('startRec');
    const stopBtn = document.getElementById('stopRec');
    const status = document.getElementById('status');
    const convoDiv = document.getElementById('conversation');
    let recognition;
    let isPolling = false;

    // === 🎤 Speech Synthesis ===
    function speakText(text) {{
      if (!window.speechSynthesis) return;
      const utter = new SpeechSynthesisUtterance(text);
      utter.rate = 1;
      utter.pitch = 1;
      utter.volume = 1;
      utter.lang = "en-IN";
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utter);
    }}

    // === 💬 Add message ===
    function addMessage(sender, text) {{
      const p = document.createElement("p");
      p.innerHTML = `<b>${{sender}}:</b> ${{text}}`;
      convoDiv.appendChild(p);
      convoDiv.scrollTop = convoDiv.scrollHeight;
    }}

    // === 🔁 Poll Supervisor (async reliable) ===
    async function pollSupervisor(requestId) {{
      if (isPolling) return; // prevent multiple loops
      isPolling = true;
      console.log("🕓 Polling supervisor for response...");
      status.innerText = "⏳ Waiting for supervisor response...";

      while (isPolling) {{
        try {{
          const res = await fetch("{DJANGO_FOLLOWUP_API}" + requestId + "/");
          const data = await res.json();

          if (res.status === 200 && data.source === "supervisor") {{
            console.log("✅ Supervisor replied:", data.answer);
            addMessage("👨‍💼 Supervisor", data.answer);

            const followupVoice = "My supervisor has just responded. " + data.answer;
            addMessage("🤖 AI", "My supervisor says: " + data.answer);
            speakText(followupVoice);

            status.innerText = "✅ Supervisor responded.";
            isPolling = false;
            break;
          }}
        }} catch (err) {{
          console.error("Polling error:", err);
        }}
        await new Promise(r => setTimeout(r, 2000)); // wait 2s before next check
      }}
    }}

    // === 🎙️ Speech Recognition ===
    if (!('webkitSpeechRecognition' in window)) {{
        status.innerText = "⚠️ Browser does not support speech recognition.";
    }} else {{
        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = "en-IN";

        recognition.onstart = () => {{
            status.innerText = "🎙️ Listening...";
            startBtn.style.display = "none";
            stopBtn.style.display = "inline-block";
        }};

        recognition.onresult = async (event) => {{
            let transcript = "";
            for (let i = event.resultIndex; i < event.results.length; ++i) {{
                transcript += event.results[i][0].transcript;
            }}

            if (event.results[event.results.length - 1].isFinal) {{
                addMessage("🧑 You", transcript);
                status.innerText = "💬 Sending to AI...";

                try {{
                    const res = await fetch("{DJANGO_CHAT_API}", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify({{
                            customer_id: 1,
                            question: transcript
                        }})
                    }});

                    const data = await res.json();

                    if (res.ok && res.status === 200) {{
                        addMessage("🤖 AI", data.answer);
                        speakText(data.answer);
                        status.innerText = "✅ AI responded.";
                    }} 
                    else if ((res.status === 202 || res.status === 200) && data.source === "pending") {{
                        addMessage("🤖 AI", data.answer);
                        speakText(data.answer);
                        status.innerText = "⏳ Waiting for supervisor...";
                        if (data.request_id) pollSupervisor(data.request_id);
                    }} 
                    else {{
                        addMessage("⚠️ Error", data.detail || "Something went wrong.");
                    }}
                }} catch (err) {{
                    addMessage("❌ Error", err.message);
                }}
            }}
        }};

        recognition.onerror = (e) => {{
            status.innerText = "⚠️ Error: " + e.error;
        }};

        recognition.onend = () => {{
            status.innerText = "⏹️ Stopped listening.";
            startBtn.style.display = "inline-block";
            stopBtn.style.display = "none";
        }};
    }}

    // === 🎛️ Button controls ===
    startBtn.addEventListener('click', () => recognition?.start());
    stopBtn.addEventListener('click', () => recognition?.stop());
  </script>
""", height=600)
