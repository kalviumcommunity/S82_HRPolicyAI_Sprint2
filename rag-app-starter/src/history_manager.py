import os
import sys
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.token_estimator import count_tokens

def total_tokens(messages):
    """Calculate the total tokens for a list of messages."""
    return sum(count_tokens(m["content"]) for m in messages)

def trim_history(messages, budget=150):
    """
    Trims the message history if it exceeds the token budget.
    Always preserves the system message (index 0).
    Removes the oldest non-system message until under budget.
    """
    while total_tokens(messages) > budget and len(messages) > 2:
        # Keep index 0 (system prompt), remove index 1 (oldest turn)
        removed = messages.pop(1)
        print(f"  [Trim] Removed message: {removed['role']} ({count_tokens(removed['content'])} tokens)")

def simulate_llm_response(messages):
    """
    Simulates an LLM response to demonstrate history management without needing an API key.
    """
    return "This is a simulated response acknowledging your input."

def run_conversation_demo():
    print("Starting Context Window & Message History Management Demo...")
    
    # A small budget to force trimming quickly for demonstration
    TOKEN_BUDGET = 50 
    print(f"Token Budget set to: {TOKEN_BUDGET}\n")

    system_prompt = "You are a helpful HR assistant answering questions based on company policy."
    
    history = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Simulate a conversation that is long enough to exceed the budget
    user_inputs = [
        "What is the company policy on annual leave?",
        "Can I carry over unused leave to the next year?",
        "How do I apply for parental leave?",
        "Is there a limit to sick days?",
        "What about bereavement leave? Could you give me all the details?"
    ]
    
    for i, user_msg in enumerate(user_inputs, 1):
        print(f"\n--- Turn {i} ---")
        history.append({"role": "user", "content": user_msg})
        
        pre_trim_tokens = total_tokens(history)
        print(f"Tokens before trim: {pre_trim_tokens}")
        
        # Trim history to stay within budget
        trim_history(history, budget=TOKEN_BUDGET)
        
        post_trim_tokens = total_tokens(history)
        print(f"Tokens after trim: {post_trim_tokens}")
        
        # Simulate LLM call (or real LLM call if implemented)
        # response_text = call_llm(history)
        response_text = simulate_llm_response(history)
        
        history.append({"role": "assistant", "content": response_text})
        
        print(f"Assistant: {response_text}")

if __name__ == "__main__":
    run_conversation_demo()
