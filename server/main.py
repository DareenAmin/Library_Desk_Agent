# /server/main.py (FINAL VERSION WITH DB HISTORY PERSISTENCE)

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Dict, Any, List, Union
from langchain_core.messages import HumanMessage, AIMessage

# --- New Imports ---
# Import the helper functions for DB operations
from db_tools import load_history, save_message
from agent import create_library_agent, run_agent_chat, LibraryAgent

# --- Global Agent State ---
AGENT: Union[LibraryAgent, None] = create_library_agent()

# --- Pydantic Data Model for Request Body ---
class ChatRequest(BaseModel):
    prompt: str
    session_id: str

# --- FastAPI App Initialization ---
app = FastAPI(title="Library Desk Agent API")

# --- CORS Middleware Configuration (Remains the same) ---
origins = [
    "http://localhost",
    "http://localhost:8501", 
    "http://127.0.0.1:8501",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoints ---

@app.get("/")
def read_root():
    status = "running" if AGENT else "Error: Agent not loaded (Check API Key)."
    return {"message": "Library Desk Agent API is running.", "agent_status": status}

# NEW ENDPOINT: To load history on Streamlit startup
@app.get("/history/{session_id}")
async def load_chat_history(session_id: str) -> Dict[str, Any]:
    """Retrieves chat history from the database for a given session."""
    db_result = load_history(session_id)
    return db_result

@app.post("/chat")
async def chat_endpoint(request: ChatRequest) -> Dict[str, Any]:
    user_prompt = request.prompt
    session_id = request.session_id
    
    if not AGENT:
        return {
            "response": "Agent failed to initialize. Check API Key.",
            "session_id": session_id,
            "tool_info": {}
        }

    # 1. Load History (Convert DB dicts to LangChain messages)
    db_history_result = load_history(session_id)
    history_lc: List[Union[HumanMessage, AIMessage]] = []
    
    if db_history_result['status'] == 'Success':
        for msg in db_history_result['history']:
            if msg['role'] == 'user':
                history_lc.append(HumanMessage(content=msg['content']))
            else:
                history_lc.append(AIMessage(content=msg['content']))

    # 2. Save User Message to DB
    save_message(session_id, 'user', user_prompt)
    
    # 3. Run the Agent with loaded history
    ai_response_message: AIMessage = run_agent_chat(AGENT, user_prompt, history_lc)
    ai_response_content = ai_response_message.content

    # 4. Save Agent Message to DB
    save_message(session_id, 'assistant', ai_response_content)

    # 5. Prepare Response for Streamlit
    tool_status_text = "Agent processed the request (DB used for history)."

    return {
        "response": ai_response_content,
        "session_id": session_id,
        "tool_info": tool_status_text 
    }

# --- Running the Server ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)