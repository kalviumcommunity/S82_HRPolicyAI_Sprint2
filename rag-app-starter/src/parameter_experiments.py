import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

load_dotenv(dotenv_path=BASE_DIR / ".env")

def get_client():
    base_url = os.getenv("OPENAI_BASE_URL", os.getenv("API_BASE_URL"))
    api_key = os.getenv("OPENAI_API_KEY")
    if base_url and api_key:
        return OpenAI(base_url=base_url, api_key=api_key)
    return None

def run_parameter_experiments():
    client = get_client()
    model = os.getenv("CHAT_MODEL", "gpt-3.5-turbo")
    
    prompt = "Explain the importance of regular employee performance reviews in one short paragraph."
    messages = [{"role": "user", "content": prompt}]
    
    results = {}
    
    print("--- Model Parameters & Output Control Experiments ---")
    
    # Task 1: Vary temperature
    print("\n[Task 1] Testing Temperature:")
    results["temperature"] = {}
    for temp in [0.0, 1.0]:
        print(f"\nRunning with temperature={temp}...")
        try:
            if client:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temp
                )
                output = response.choices[0].message.content
            else:
                # Simulated responses for demonstration if no API key
                if temp == 0.0:
                    output = "[SIMULATED - temp=0.0] Regular performance reviews are essential for aligning employee goals with company objectives, providing constructive feedback, and identifying areas for professional development. They ensure consistent communication and help maintain productivity."
                else:
                    output = "[SIMULATED - temp=1.0] Imagine a ship without a compass—that's a company without performance reviews! They totally transform the workplace by sparking amazing conversations, boosting morale sky-high, and unleashing the hidden potential of every single team member in unexpected ways!"
            
            results["temperature"][str(temp)] = output
            print(f"Output (temp={temp}): {output}")
        except Exception as e:
            print(f"API Error: {e}")
    
    # Task 2: Cap length with max_tokens
    print("\n[Task 2] Testing max_tokens:")
    max_tokens_val = 15
    print(f"\nRunning with max_tokens={max_tokens_val}...")
    try:
        if client:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,
                max_tokens=max_tokens_val
            )
            output = response.choices[0].message.content
        else:
            output = "[SIMULATED] Regular performance reviews are essential for aligning employee goals with company"
        results["max_tokens"] = output
        print(f"Output (max_tokens={max_tokens_val}): {output}")
    except Exception as e:
        print(f"API Error: {e}")

    # Task 3: Test stop sequence
    print("\n[Task 3] Testing stop sequence:")
    stop_seq = [","]
    print(f"\nRunning with stop={stop_seq} (should stop at the first comma)...")
    try:
        if client:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,
                stop=stop_seq
            )
            output = response.choices[0].message.content
        else:
            output = "[SIMULATED] Regular performance reviews are essential for aligning employee goals with company objectives"
        results["stop_sequence"] = output
        print(f"Output (stop={stop_seq}): {output}")
    except Exception as e:
        print(f"API Error: {e}")

    # Save outputs
    output_dir = BASE_DIR / "outputs"
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / "parameter_experiments.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
        
    print("\nExperiments completed. Results saved to outputs/parameter_experiments.json")

if __name__ == "__main__":
    run_parameter_experiments()
