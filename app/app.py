# /app/app.py (Complete Code for Streamlit Frontend)

import streamlit as st
import requests  # To communicate with the FastAPI backend
import uuid
from typing import Dict, Any, List

# --- Configuration ---
st.set_page_config(page_title="Library Desk Agent", layout="wide")
API_URL = "http://localhost:8000/chat"
HISTORY_URL = "http://localhost:8000/history"


## 1. Helper Functions to Communicate with Backend
def send_message_to_agent(user_prompt: str, session_id: str) -> Dict[str, Any]:
    """
    Sends the user prompt and session ID to the FastAPI agent endpoint.
    """
    try:
        response = requests.post(
            API_URL, 
            json={"prompt": user_prompt, "session_id": session_id},
            timeout=30 # Set a reasonable timeout for the LLM
        )
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        # Handle connection errors, timeouts, etc.
        return {
            "response": f"Error communicating with the agent server at {API_URL}. Is the backend running? Details: {e}",
            "tool_info": "Connection Error",
            "session_id": session_id
        }

def load_chat_history(session_id: str) -> List[Dict[str, Any]]:
    """Loads chat history from the new backend endpoint."""
    try:
        response = requests.get(f"{HISTORY_URL}/{session_id}")
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "Success":
            loaded_messages = []
            for msg in data['history']:
                # Reconstruct the Streamlit message format for display
                loaded_messages.append({
                    "role": msg['role'],
                    "content": msg['content'],
                    # Use a placeholder for tool_info for messages loaded from DB
                    "tool_info": "Loaded from DB" if msg['role'] == 'assistant' else None
                })
            return loaded_messages
        return []
    except requests.exceptions.RequestException:
        st.error("Could not connect to the backend to load history. Please ensure the server is running.")
        return []

## 2. Session State Initialization (With Persistence)
if "session_id" not in st.session_state:
    # Generate a unique ID for the chat session
    st.session_state["session_id"] = str(uuid.uuid4())

# Load history only on the initial run (after a full page reload)
if "messages" not in st.session_state:
    st.session_state["messages"] = load_chat_history(st.session_state["session_id"])


## 3. Title and Session Selector
st.title("📚 Library Desk Agent")

with st.sidebar:
    st.header("Chat Session")
    st.markdown(f"Current Session ID: **{st.session_state['session_id']}**")
    
    # Button to start a new chat (resets Streamlit state and uses a new session_id)
    if st.button("Start New Chat"):
        st.session_state["messages"] = []
        st.session_state["session_id"] = str(uuid.uuid4())
        # The old session history remains in the DB, but a new ID ensures a clean slate
        st.rerun() 


## 4. Display Chat History
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            # Display Tool Status for transparency
            st.markdown(f"**Tool Status:** `{message['tool_info']}`")
            st.markdown("---")
            st.markdown(message["content"])
        else:
            st.markdown(message["content"])


## 5. Handle User Input
if user_prompt := st.chat_input("Ask the Library Agent..."):
    
    # 1. Add user message to state and display
    st.session_state["messages"].append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # 2. Get agent response from the backend
    with st.spinner("Agent is thinking and checking inventory..."):
        agent_response_data = send_message_to_agent(
            user_prompt, 
            st.session_state["session_id"]
        )
        
        agent_response = agent_response_data.get("response", "An unknown error occurred.")
        tool_info = agent_response_data.get("tool_info", "No status info.")

    # 3. Add agent response to state and display
    ai_message_data = {
        "role": "assistant", 
        "content": agent_response,
        "tool_info": tool_info # Store tool info to display later
    }
    
    st.session_state["messages"].append(ai_message_data)
    with st.chat_message("assistant"):
        st.markdown(f"**Tool Status:** `{tool_info}`")
        st.markdown("---")
        st.markdown(agent_response)