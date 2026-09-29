from flask import Flask, render_template, request, jsonify
import requests
import os
import time
import random
import threading

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = "models/gemini-3-flash-preview"

SYSTEM_PROMPT = """
Sen BenimAI adlı yapay zekâ asistanısın.

Kurallar:
- Her zaman Türkçe konuş.
- Soruyu dikkatlice analiz et.
- Mantıklı, doğru ve anlaşılır cevaplar ver.
- Gereksiz tekrar yapma.
- Kullanıcı kısa sorarsa kısa cevap ver.
- Kullanıcı detay isterse detaylı anlat.
- Emin olmadığın bilgileri kesin doğruymuş gibi söyleme.
- Matematik işlemlerini kontrol et.
- Kod sorularında çalışabilir ve anlaşılır kod vermeye çalış.
- Önceki konuşmadaki bilgileri dikkate al.
- Doğal ve samimi konuş.
- Kendini Google Gemini olarak tanıtma.
- Kendini BenimAI olarak tanıt.
"""

gemini_lock = threading.Lock()


def ai_cevap(messages):

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY bulunamadı.")

    url = f"https://generativelanguage.googleapis.com/v1beta/{MODEL}:generateContent"

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

        gemini_role = "model" if role == "model" else "user"

        contents.append({
            "role": gemini_role,
            "parts": [
                {
                    "text": content
                }
            ]
        })

    if not contents:
        raise ValueError("Mesaj içeriği boş.")

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

    with gemini_lock:

        max_retries = 3

        for attempt in range(max_retries):

            try:

                response = requests.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=120
                )

                print("GEMINI STATUS:", response.status_code)

                if response.status_code == 200:

                    sonuc = response.json()

                    candidates = sonuc.get("candidates", [])

                    if not candidates:
                        raise RuntimeError(
                            "Gemini cevap oluşturamadı."
                        )

                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])

                    if not parts:
                        raise RuntimeError(
                            "Gemini boş cevap gönderdi."
                        )

                    return parts[0].get("text", "").strip()

                if response.status_code == 429:

                    print(
                        f"GEMINI 429 - Deneme "
                        f"{attempt + 1}/{max_retries}"
                    )

                    if attempt < max_retries - 1:

                        wait_time = (2 ** (attempt + 1)) + random.uniform(
                            0, 1
                        )

                        time.sleep(wait_time)
                        continue

                    raise RuntimeError(
                        "Gemini kullanım limitine ulaşıldı. "
                        "Lütfen biraz sonra tekrar dene."
                    )

                if 500 <= response.status_code < 600:

                    print(
                        f"GEMINI {response.status_code} - "
                        f"Deneme {attempt + 1}/{max_retries}"
                    )

                    if attempt < max_retries - 1:

                        wait_time = (2 ** (attempt + 1)) + random.uniform(
                            0, 1
                        )

                        time.sleep(wait_time)
                        continue

                    raise RuntimeError(
                        "Gemini şu anda cevap veremiyor. "
                        "Lütfen biraz sonra tekrar dene."
                    )

                print("GEMINI RESPONSE:", response.text)

                response.raise_for_status()

            except requests.exceptions.Timeout:

                print(
                    f"GEMINI TIMEOUT - "
                    f"Deneme {attempt + 1}/{max_retries}"
                )

                if attempt < max_retries - 1:
                    time.sleep(2 ** (attempt + 1))
                    continue

                raise RuntimeError(
                    "Gemini yanıt vermek için çok uzun süre bekledi."
                )

            except requests.exceptions.RequestException as e:

                print("GEMINI API HATASI:", repr(e))
                raise

    raise RuntimeError("Gemini isteği başarısız oldu.")


@app.route("/")
def ana_sayfa():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "error": "İstek verisi alınamadı."
            }), 400

        messages = data.get("messages")

        if not messages:

            eski_mesaj = data.get(
                "message",
                ""
            ).strip()

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

    except RuntimeError as e:

        mesaj = str(e)

        print("BENIMAI HATASI:", mesaj)

        if "limitine" in mesaj:
            return jsonify({
                "error": mesaj
            }), 429

        return jsonify({
            "error": mesaj
        }), 500

    except requests.exceptions.HTTPError as e:

        print("GEMINI HTTP HATASI:", repr(e))

        return jsonify({
            "error": "Yapay zekâ servisine şu anda ulaşılamıyor."
        }), 503

    except requests.exceptions.RequestException as e:

        print("GEMINI API HATASI:", repr(e))

        return jsonify({
            "error": "Yapay zekâ servisine bağlanırken bir sorun oluştu."
        }), 503

    except Exception as e:

        print("CHAT HATASI:", repr(e))

        return jsonify({
            "error": "BenimAI şu anda cevap veremedi."
        }), 500


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )
