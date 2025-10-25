import requests

# ✅ Correct base URLs
BASE_URL = "http://127.0.0.1:8000"
CHAT_URL = f"{BASE_URL}/api/chat/"
SUPERVISOR_URL = f"{BASE_URL}/api/supervisorresponses/"
KNOWLEDGE_BASE_URL = f"{BASE_URL}/api/knowledge-base/"

def chat_with_agent(customer_id, question):
    try:
        response = requests.post(f"{BASE_URL}/api/chat/", json={
            "customer_id": customer_id,
            "question": question
        })

        # Handle all valid responses explicitly
        if response.status_code == 200:
            return response.json()

        elif response.status_code == 202:
            # AI is escalating to supervisor
            data = response.json()
            return {
                "answer": data.get("answer", "Please wait, let me connect with supervisor…"),
                "source": "pending",
                "request_id": data.get("request_id")
            }

        elif response.status_code == 400:
            return {"error": "Bad request: Missing question or customer_id."}

        else:
            return {"error": f"Chat API returned {response.status_code}"}

    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}
    
def get_supervisor_responses():
    try:
        response = requests.get(SUPERVISOR_URL)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []

def post_supervisor_response(data):
    try:
        response = requests.post(SUPERVISOR_URL, json=data)
        return response.status_code == 201
    except Exception:
        return False

def get_knowledge_base():
    try:
        response = requests.get(KNOWLEDGE_BASE_URL)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []
