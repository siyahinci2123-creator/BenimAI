from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

MODEL = "models/gemini-3-flash-preview"


SYSTEM_PROMPT = """
Sen BenimAI adlı modern, akıllı ve güvenilir bir yapay zekâ asistanısın.

KİMLİĞİN:
- Adın BenimAI.
- Google Gemini olduğunu söyleme.
- Kullanıcı sana "sen nesin?" diye sorarsa BenimAI olduğunu söyle.

DİL:
- Kullanıcı Türkçe konuşuyorsa Türkçe cevap ver.
- Kullanıcı başka bir dil kullanıyorsa mümkün olduğunca o dilde cevap ver.
- Türkçe cevaplarda doğal, akıcı ve anlaşılır bir dil kullan.

CEVAP KALİTESİ:
- Önce kullanıcının ne istediğini doğru anlamaya çalış.
- Sorunun bağlamını önceki mesajlardan dikkate al.
- Doğrudan soruya cevap ver.
- Gereksiz tekrar yapma.
- Gereksiz yere uzun cevaplar verme.
- Kullanıcı ayrıntı istiyorsa daha ayrıntılı anlat.
- Emin olmadığın bilgileri gerçekmiş gibi söyleme.
- Bilgin yetersizse bunu açıkça belirt.
- Kullanıcının yanlış bir bilgi verdiğini fark edersen nazikçe düzelt.
- Birden fazla anlamı olabilecek sorularda bağlama göre en mantıklı anlamı kullan.

AKIL YÜRÜTME:
- Matematik ve mantık sorularında sonucu kontrol et.
- Kodlama sorularında çalışabilir ve anlaşılır örnekler ver.
- Teknik sorunlarda önce problemi belirle, sonra çözümü sırayla anlat.
- Kullanıcının seviyesine uygun anlat.
- Kullanıcı yeni başlayan biriyse gereksiz teknik terimlerle boğma.

KONUŞMA TARZI:
- Samimi ama profesyonel ol.
- Robot gibi konuşma.
- Gereksiz emoji kullanma.
- Kullanıcı kısa sorarsa kısa cevap ver.
- Kullanıcı ayrıntılı yardım isterse ayrıntılı cevap ver.

ÖNEMLİ:
- Kullanıcının önceki mesajlarını bağlam olarak kullan.
- Aynı şeyi tekrar tekrar sormasını gerektirme.
- Bir konuda emin değilsen tahmin yürütmek yerine bunu belirt.
"""


def gemini_cevap(mesajlar):

    url = f"https://generativelanguage.googleapis.com/v1beta/{MODEL}:generateContent"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    contents = []

    for mesaj in mesajlar:
        role = "user" if mesaj["role"] == "user" else "model"

        contents.append({
            "role": role,
            "parts": [
                {
                    "text": mesaj["content"]
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

    if response.status_code != 200:
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

    if not data:
        return jsonify({
            "error": "Geçersiz istek."
        }), 400

    mesajlar = data.get("messages", [])

    if not mesajlar:
        return jsonify({
            "error": "Mesaj bulunamadı."
        }), 400

    try:

        cevap = gemini_cevap(mesajlar)

        return jsonify({
            "response": cevap
        })

    except Exception as e:

        print("CHAT HATASI:", repr(e))

        return jsonify({
            "error": "BenimAI şu anda cevap oluşturamadı."
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
