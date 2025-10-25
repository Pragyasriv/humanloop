import streamlit as st
import time
import requests
from utils import chat_with_agent

BASE_URL = "http://127.0.0.1:8000"

st.title("👩‍💼 Agent and Customer Conversation")

# --- Session state setup ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pending_request" not in st.session_state:
    st.session_state.pending_request = None
if "last_agent_message" not in st.session_state:
    st.session_state.last_agent_message = None


def typing_animation(prefix, text, delay=0.03):
    placeholder = st.empty()
    shown = ""
    for c in text:
        shown += c
        placeholder.markdown(f"{prefix} {shown}")
        time.sleep(delay)
    return placeholder


customer_id = st.text_input("Customer ID", "1")
question = st.text_area("Ask your question:")

# --- On Send ---
if st.button("Send"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Agent is thinking..."):
            response = chat_with_agent(customer_id, question)

        if "error" in response:
            st.error(response["error"])
        else:
            answer = response.get("answer") or "No response available."
            source = response.get("source", "ai")
            req_id = response.get("request_id")

            # ✅ Clear previous agent message for a new question
            st.session_state.chat_history = [
                (s, t) for (s, t) in st.session_state.chat_history if s != "Agent"
            ]

            # Save current interaction
            st.session_state.chat_history.append(("Customer", question))
            st.session_state.chat_history.append(("Agent", answer))

            if source == "pending" and req_id:
                st.session_state.pending_request = req_id
                st.info("⏳ AI has escalated your question to the supervisor. Waiting for response...")


# --- Follow-up polling ---
if st.session_state.pending_request:
    req_id = st.session_state.pending_request
    for _ in range(30):          # 30 tries × 2 s ≈ 1 min
        time.sleep(2)
        r = requests.get(f"{BASE_URL}/api/chat/followup/{req_id}/")
        if r.status_code == 200:
            data = r.json()
            if data.get("source") == "supervisor":
                ans = data.get("answer", "")
                st.session_state.chat_history.append(("Supervisor", ans))
                st.session_state.pending_request = None
                typing_animation("🧠 **Agent:**", f" Supervisor says: {ans}")
                break
        # 202 → still waiting
    else:
        st.warning("Supervisor still reviewing. Please check later.")

# --- Display chat ---
st.markdown("### 💬 Conversation")
for speaker, text in st.session_state.chat_history:
    if speaker == "Customer":
        st.markdown(
            f"<div style='background-color:#2e2e2e;padding:10px;border-radius:8px;margin-bottom:4px;'>"
            f"<b>👤 You:</b> {text}</div>", unsafe_allow_html=True)
    elif speaker == "Agent":
        st.markdown(
            f"<div style='background-color:#164a41;padding:10px;border-radius:8px;margin-bottom:4px;'>"
            f"<b>🧠 Agent:</b> {text}</div>", unsafe_allow_html=True)
    elif speaker == "Supervisor":
        st.markdown(
            f"<div style='background-color:#1a3c6b;padding:10px;border-radius:8px;margin-bottom:4px;'>"
            f"<b>🧑‍🏫 Supervisor:</b> {text}</div>", unsafe_allow_html=True)
