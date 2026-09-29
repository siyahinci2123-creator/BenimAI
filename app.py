from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(**name**)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = "models/gemini-3-flash-preview"

SYSTEM_PROMPT = """
Sen BenimAI adlı yapay zekâ asistanısın.

Kurallar:

* Her zaman Türkçe konuş.
* Soruyu dikkatlice analiz et.
* Mantıklı, doğru ve anlaşılır cevaplar ver.
* Gereksiz tekrar yapma.
* Kullanıcı kısa sorarsa kısa cevap ver.
* Kullanıcı detay isterse detaylı anlat.
* Emin olmadığın bilgileri kesin doğruymuş gibi söyleme.
* Matematik işlemlerini kontrol et.
* Kod sorularında çalışabilir ve anlaşılır kod vermeye çalış.
* Önceki konuşmadaki bilgileri dikkate al.
* Doğal ve samimi konuş.
* Kendini Google Gemini olarak tanıtma.
* Kendini BenimAI olarak tanıt.
  """

def ai_cevap(messages):
url = f"https://generativelanguage.googleapis.com/v1beta/{MODEL}:generateContent"

```
headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": GEMINI_API_KEY
}

contents = []

for message in messages:
    role = message.get("role")
    content = message.get("content", "").strip()

    if not content:
        continue

    if role == "model":
        gemini_role = "model"
    else:
        gemini_role = "user"

    contents.append({
        "role": gemini_role,
        "parts": [
            {
                "text": content
            }
        ]
    })

data = {
    "system_instruction": {
        "parts": [
            {
                "text": SYSTEM_PROMPT
            }
        ]
    },
    "contents": contents,
    "generationConfig": {
        "temperature": 0.6,
        "topP": 0.9,
        "maxOutputTokens": 800
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
```

@app.route("/")
def ana_sayfa():
return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
try:
data = request.get_json(silent=True)

```
    if not data:
        return jsonify({
            "error": "İstek verisi alınamadı."
        }), 400

    messages = data.get("messages")

    if not messages:
        eski_mesaj = data.get("message", "").strip()

        if eski_mesaj:
            messages = [
                {
                    "role": "user",
                    "content": eski_mesaj
                }
            ]

    if not messages:
        return jsonify({
            "error": "Mesaj bulunamadı."
        }), 400

    cevap = ai_cevap(messages)

    return jsonify({
        "response": cevap
    })

except requests.exceptions.RequestException as e:
    print("GEMINI API HATASI:", repr(e))

    return jsonify({
        "error": f"Gemini API hatası: {str(e)}"
    }), 500

except Exception as e:
    print("CHAT HATASI:", repr(e))

    return jsonify({
        "error": f"Sunucu hatası: {str(e)}"
    }), 500
```

if **name** == "**main**":
app.run(
host="0.0.0.0",
port=5000
)
