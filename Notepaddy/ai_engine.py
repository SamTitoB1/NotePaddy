import subprocess
import requests
import os

def is_ollama_running():
    try:
        requests.get("http://localhost:11434")
        return True
    except:
        return False

def start_ollama():
    bat_path = os.path.join(os.path.dirname(__file__), "run_ai_server.bat")
    subprocess.Popen(bat_path, shell=True)

def ask_ollama(prompt, model="llama2:7b"):
    if not is_ollama_running():
        start_ollama()
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        )
        return response.json().get("response", "⚠️ No valid response key.")
    except Exception as e:
        return f"⚠️ AI Error: {e}"