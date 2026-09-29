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
        "topP": 0.
```
