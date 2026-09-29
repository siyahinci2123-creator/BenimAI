from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


def ai_cevap(mesaj):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"""Sen BenimAI adlı hızlı ve doğal konuşan bir yapay zekâ asistanısın.

Kurallar:
- Her zaman Türkçe konuş.
- Doğal ve düzgün cümleler kur.
- Kullanıcının sorusuna doğrudan cevap ver.
- Gereksiz yere uzun cevaplar verme.
- Kendini Google Gemini veya başka bir şirketin asistanı olarak tanıtma.
- Kendini BenimAI olarak tanıt.
- Emin olmadığın bilgileri kesinmiş gibi söyleme.

Kullanıcı: {mesaj}

BenimAI:"""
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 500
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=120
    )

    response.raise_for_status()

    sonuc = response.json()

    return sonuc["candidates"][0]["content"]["parts"][0]["text"]


@app.route("/")
def ana_sayfa():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    mesaj = data.get("message", "").strip()

    if not mesaj:
        return jsonify({"error": "Mesaj boş olamaz."})

    try:
        cevap = ai_cevap(mesaj)
        return jsonify({"response": cevap})
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
