from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)


def ai_cevap(mesaj):
    response = requests.post(
        "http://127.0.0.1:11434/api/generate",
        json={
            "model": "qwen2.5:3b",
            "prompt": f"""Sen BenimAI adlı hızlı ve doğal konuşan bir yapay zekâ asistanısın.

Kurallar:
- Her zaman Türkçe konuş.
- Doğal ve düzgün cümleler kur.
- Devrik cümlelerden kaçın.
- Kısa ve anlaşılır cevaplar ver.
- Kullanıcının sorusuna doğrudan cevap ver.
- Gereksiz tekrar ve uzun açıklamalar yapma.
- Kendini Alibaba Cloud veya başka bir şirketin asistanı olarak tanıtma.
- Emin olmadığın bilgileri kesinmiş gibi söyleme.
- Mümkün olduğunca hızlı ve net cevap ver.

Kullanıcı: {mesaj}

BenimAI:""",
            "stream": False,
            "options": {
                "num_predict": 80,
                "temperature": 0.7
            }
        },
        timeout=120
    )

    response.raise_for_status()
    return response.json()["response"]


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
    app.run(host="127.0.0.1", port=5000, debug=True)