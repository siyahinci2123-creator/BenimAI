from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


def ai_cevap(mesaj):
    url = "https://generativelanguage.googleapis.com/v1beta/models"

    headers = {
        "x-goog-api-key": GEMINI_API_KEY
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=60
    )

    print("MODELLER STATUS:", response.status_code)
    print("MODELLER RESPONSE:", response.text)

    response.raise_for_status()

    modeller = response.json().get("models", [])

    uygun_modeller = []

    for model in modeller:
        methods = model.get("supportedGenerationMethods", [])

        if "generateContent" in methods:
            uygun_modeller.append(model.get("name"))

    print("GENERATECONTENT MODELLERI:", uygun_modeller)

    if not uygun_modeller:
        raise Exception("generateContent destekleyen model bulunamadı.")

    # İlk kullanılabilir modeli seç
    model_adi = uygun_modeller[0]

    generate_url = f"https://generativelanguage.googleapis.com/v1beta/{model_adi}:generateContent"

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"""Sen BenimAI adlı yapay zekâ asistanısın.

Her zaman Türkçe konuş.
Doğal ve anlaşılır cevaplar ver.
Kullanıcının sorusuna doğrudan cevap ver.
Gereksiz yere uzun cevaplar verme.
Kendini Google Gemini olarak tanıtma.
Kendini BenimAI olarak tanıt.

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
        generate_url,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        },
        json=data,
        timeout=120
    )

    print("GEMINI STATUS:", response.status_code)
    print("GEMINI RESPONSE:", response.text)

    response.raise_for_status()

    sonuc = response.json()

    return sonuc["candidates"][0]["content"]["parts"][0]["text"]
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
                        "text": f"""Sen BenimAI adlı yapay zekâ asistanısın.

Kurallar:
- Her zaman Türkçe konuş.
- Doğal ve anlaşılır cevaplar ver.
- Kullanıcının sorusuna doğrudan cevap ver.
- Gereksiz yere uzun cevaplar verme.
- Kendini Google Gemini olarak tanıtma.
- Kendini BenimAI olarak tanıt.

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

    print("GEMINI STATUS:", response.status_code)
    print("GEMINI RESPONSE:", response.text)

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
        print("CHAT HATASI:", repr(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
