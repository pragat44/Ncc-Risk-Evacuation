# In src/matcher_llama.py

import ollama
import json

def reason_with_llama(contract_segment: str, ncc_description: str) -> dict:
    """
    Uses a local Llama model via Ollama to provide a risk judgment.
    """
    # This prompt instructs the model on its role, the task, and the output format.
    prompt = f"""
    You are a risk analysis expert. Your task is to determine if a new contract requirement
    fully mitigates a known past failure.

    - Contract Requirement: "{contract_segment}"
    - Past Failure: "{ncc_description}"

    Analyze if the requirement resolves the failure. Respond with ONLY a single, valid
    JSON object with two keys: "risk_judgment" (either "Risk Mitigated", "Risk Identified",
    or "Uncertain") and "reasoning" (a brief explanation).
    """

    try:
        # This is the connection to Ollama.
        response = ollama.chat(
            model='llama3',       # The model running in Ollama
            messages=[{'role': 'user', 'content': prompt}],
            format='json'         # This ensures the output is a JSON string
        )

        # The library helps parse the JSON response from the model
        result_json = json.loads(response['message']['content'])
        return result_json

    except Exception as e:
        # Handle cases where the connection to Ollama fails
        print(f"Error connecting to Ollama: {e}")
        return {
            "risk_judgment": "Error",
            "reasoning": "Failed to connect to the Llama model."
        }