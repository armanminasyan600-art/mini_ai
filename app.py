from flask import Flask, request, jsonify, send_from_directory
import requests
import traceback
import re

app = Flask(__name__)

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "gpt-oss:20b-cloud"

SYSTEM_PROMPT = (
    "You are Mini.AI, a friendly assistant. "
    "Always answer in the language the user writes in. "
    "If the user writes Armenian using Latin letters, answer in Armenian letters. "
    "If the user writes Russian using Latin letters, answer in Russian Cyrillic. "
    "Keep answers clear, natural, and short. "
    "Do not use Markdown math, LaTeX, $$, or boxed formatting unless specifically asked. "
    "For normal conversation, use plain text."
)

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        message = data.get("message", "").strip()

        if not message:
            return jsonify({"error": "Message is empty"}), 400

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "stream": False,
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            },
            timeout=300
        )

        response.raise_for_status()

        result = response.json()
        reply = result["message"]["content"]

        reply = re.sub(
            r"<think>.*?</think>",
            "",
            reply,
            flags=re.DOTALL | re.IGNORECASE
        ).strip()

        return jsonify({"reply": reply})

    except requests.exceptions.ConnectionError:
        return jsonify({
            "error": "Չհաջողվեց կապվել Ollama-ի հետ։"
        }), 500

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Ollama-ն շատ երկար ժամանակ չպատասխանեց։"
        }), 500

    except Exception as e:
        print("\n========== ERROR ==========")
        traceback.print_exc()
        print("===========================\n")

        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    print("Mini AI started!")
    print("Ollama:", OLLAMA_URL)
    print("Model:", MODEL)
    print("Open: http://127.0.0.1:5000")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )