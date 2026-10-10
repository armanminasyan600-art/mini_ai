
from flask import Flask, request, jsonify, send_from_directory
import requests

app = Flask(__name__)

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "gemma4:e2b"

SYSTEM_PROMPT = """
Դու Mini.AI-ն ես՝ արագ և ճշգրիտ AI օգնական։
Պատասխանիր օգտատիրոջ լեզվով։
Սկզբում տուր ուղիղ պատասխանը։
Պատասխանիր կարճ ու պարզ, եթե մանրամասն չեն խնդրել։
Մի կրկնիր հարցը և մի հորինիր փաստեր։
Ծրագրավորման հարցերին տուր ճիշտ, աշխատող օրինակներ։
"""

@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Գրիր հաղորդագրություն։"}), 400

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message.strip()}
                ],
                "stream": False,
                "keep_alive": -1,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 100,
                    "num_ctx": 1024
                }
            },
            timeout=180
        )

        if response.status_code != 200:
            return jsonify({
                "error": "Ollama-ի սխալ։ Ստուգիր մոդելը։",
                "details": response.text[:300]
            }), 502

        result = response.json()
        answer = result.get("message", {}).get("content", "").strip()

        if not answer:
            return jsonify({"error": "Պատասխան չստացվեց։"}), 502

        return jsonify({"response": answer})

    except requests.exceptions.ConnectionError:
        return jsonify({
            "error": "Ollama-ն միացված չէ։ Բացիր Ollama-ն։"
        }), 503

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Պատասխանը ուշացավ։ Փորձիր կրկին։"
        }), 504

    except Exception:
        app.logger.exception("Mini.AI error")
        return jsonify({"error": "Ներքին սխալ։ Ստուգիր CMD-ն։"}), 500


if __name__ == "__main__":
    print("Mini.AI-ն պատրաստ է։")
    print("Բացիր՝ http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
