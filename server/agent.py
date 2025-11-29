from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env

import os
import json
from typing import List, Dict, Union, Any

# Modern LangChain imports
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

# Local DB Tools
from db_tools import find_books, create_order, restock_book, update_price, order_status, inventory_summary

# --- 1. Define Tools for LangChain ---

@tool
def find_books_tool(q: str, by: str = "title") -> str:
    """Finds books by title or author based on the search query (q). Searches are partial matches."""
    return json.dumps(find_books(q, by))

@tool
def create_order_tool(customer_id: int, items: List[Dict[str, Union[str, int]]]) -> str:
    """
    Creates a new order, adds items (list of {'isbn': str, 'qty': int}), and reduces stock.
    Requires customer_id (int) and a list of items to sell (list of {'isbn': str, 'qty': int}).
    """
    return json.dumps(create_order(customer_id, items))

@tool
def restock_book_tool(isbn: str, qty: int) -> str:
    """Restocks a book by adding the given quantity (qty: int) and returns the new stock level."""
    return json.dumps(restock_book(isbn, qty))

@tool
def update_price_tool(isbn: str, price: float) -> str:
    """Updates the price (price: float) of a book specified by ISBN."""
    return json.dumps(update_price(isbn, price))

@tool
def order_status_tool(order_id: int) -> str:
    """Retrieves the status, customer, and item details of an order specified by order_id (int)."""
    return json.dumps(order_status(order_id))

@tool
def inventory_summary_tool() -> str:
    """Provides a total summary of inventory quantity and lists any titles currently low in stock (stock <= 5)."""
    return json.dumps(inventory_summary())

# List of all tools the agent can use
TOOLS = [
    find_books_tool, 
    create_order_tool, 
    restock_book_tool, 
    update_price_tool, 
    order_status_tool, 
    inventory_summary_tool
]


# --- 2. Load Prompt and Initialize LLM ---
try:
    with open("../prompts/system_prompt.txt", "r") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    SYSTEM_PROMPT = ''''
   You are a functional, non-conversational, transactional AI Agent. Your sole purpose is to process the user's request, execute the necessary tools, and then output a concise, human-readable summary of the actions taken and the final updated values.

**STRICT FORMATTING AND STYLE RULES:**
1.  **NEVER** use headings (##) or Markdown tables.
2.  Combine all tool results into a single, straightforward summary paragraph or a brief list.
3.  Focus ONLY on the updated status (e.g., Order ID, new stock levels, updated price, or search results).
4.  Do not include any conversational phrases like "Here is the result," "I have processed your request," or "Let me know if you have other questions."
5.  Use **bold** text to highlight key identifiers (like Order IDs) and final numerical values (like new stock counts).

**Example Output Style:**
"The restock of The Pragmatic Programmer was successful. New stock level is **75**. Books by Andrew Hunt: The Pragmatic Programmer (ISBN: 978-0134494166)."
'''
# Initialize LLM based on environment
GEMINI_KEY = os.getenv("GOOGLE_API_KEY")

if GEMINI_KEY:
    LLM = ChatGoogleGenerativeAI(
        model=os.getenv("LLM_MODEL", "gemini-2.0-flash-exp"),
        api_key=GEMINI_KEY,
        temperature=0
    )
else:
    print("Warning: GOOGLE_API_KEY not found in environment. Agent will not function.")
    LLM = None


# --- 3. Simple Agent Implementation ---

class LibraryAgent:
    """Simple agent that uses LLM with tool calling."""
    
    def __init__(self, llm, tools, system_prompt):
        self.llm = llm
        self.tools = tools
        self.system_prompt = system_prompt
        
        # Create a tool map for easy lookup
        self.tool_map = {tool.name: tool for tool in tools}
        
        # Bind tools to the LLM
        self.llm_with_tools = self.llm.bind_tools(tools)
    
    def run(self, user_input: str, chat_history: List = None) -> str:
        """Execute the agent for one turn."""
        if chat_history is None:
            chat_history = []
        
        # Prepare messages
        messages = [SystemMessage(content=self.system_prompt)] + chat_history + [HumanMessage(content=user_input)]
        
        # Agent loop (max 10 iterations to prevent infinite loops)
        for iteration in range(10):
            # Call the LLM
            response = self.llm_with_tools.invoke(messages)
            
            # Check if there are tool calls
            if not response.tool_calls:
                # No more tool calls, return the final answer
                return response.content
            
            # Add AI response to messages
            messages.append(response)
            
            # Execute each tool call
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                print(f"\n[Tool Call] {tool_name} with args: {tool_args}")
                
                try:
                    # Get the tool and execute it
                    selected_tool = self.tool_map[tool_name]
                    tool_output = selected_tool.invoke(tool_args)
                    print(f"[Tool Output] {tool_output[:200]}...")  # Print first 200 chars
                    
                    # Add tool result to messages
                    from langchain_core.messages import ToolMessage
                    messages.append(
                        ToolMessage(
                            content=tool_output,
                            tool_call_id=tool_call["id"]
                        )
                    )
                except Exception as e:
                    error_msg = f"Error executing tool {tool_name}: {str(e)}"
                    print(f"[Error] {error_msg}")
                    from langchain_core.messages import ToolMessage
                    messages.append(
                        ToolMessage(
                            content=error_msg,
                            tool_call_id=tool_call["id"]
                        )
                    )
        
        return "Maximum iterations reached. Please try rephrasing your question."


def create_library_agent():
    """Creates and returns the Library Agent."""
    if not LLM:
        return None
    
    return LibraryAgent(LLM, TOOLS, SYSTEM_PROMPT)


def run_agent_chat(agent, user_prompt: str, history: List[Any]):
    """
    Handles a single turn of the agent interaction, including passing history.
    """
    if not agent:
        return AIMessage(content="Agent is not initialized. Check your API Key configuration.")

    try:
        # Run the agent
        response = agent.run(user_prompt, history)
        return AIMessage(content=response)
    
    except Exception as e:
        return AIMessage(content=f"An internal error occurred during agent execution: {str(e)}")


# --- 4. Minimal Run Script for Testing ---
if __name__ == "__main__":
    agent = create_library_agent()
    
    if agent:
        print("--- Library Desk Agent Initialized (Type 'exit' to quit) ---")
        history = []
        
        while True:
            user_input = input("\nUser: ")
            if user_input.lower() == 'exit':
                break

            resp_msg = run_agent_chat(agent, user_input, history)
            print(f"\nAgent: {resp_msg.content}")

            # Update history for the next turn
            history.append(HumanMessage(content=user_input))
            history.append(resp_msg)

    else:
        print("Agent could not be started. Check API keys and ensure all modules are installed.")