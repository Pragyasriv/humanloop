import streamlit as st
#from humanloop.streamlit_app.utils import get_supervisor_responses, post_supervisor_response
#from streamlit_app.utils import get_supervisor_responses, post_supervisor_response
from utils import get_supervisor_responses, post_supervisor_response



st.title("🧑‍🏫 Supervisor Dashboard")

responses = get_supervisor_responses()

if not responses:
    st.info("No pending supervisor requests found.")
else:
    for item in responses:
        st.subheader(f"Question: {item.get('question', 'N/A')}")
        answer = st.text_area(f"Provide answer for ID {item.get('id')}", "")
        if st.button(f"Submit answer for ID {item.get('id')}", key=item.get('id')):
            data = {"id": item.get("id"), "answer": answer}
            if post_supervisor_response(data):
                st.success("Response submitted successfully!")
            else:
                st.error("Failed to submit response.")
