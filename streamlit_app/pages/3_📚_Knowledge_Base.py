import streamlit as st
from utils import get_knowledge_base

st.title("📚 Knowledge Base Entries")

entries = get_knowledge_base()

if not entries:
    st.warning("No entries found in the knowledge base.")
else:
    for e in entries:
        question = e.get('question', 'N/A')
        answer = e.get('answer', 'N/A')
        st.markdown(f"**ID:** {e.get('id')} | **Question:** {question}")
        st.write(f"**Answer:** {answer}")
        st.divider()
