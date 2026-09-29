from flask import Flask, render_template, request, jsonify
import requests
import os
import time
import random
import threading

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

# Aynı anda birden fazla Gemini isteği gönderilmesini engeller.

gemini_lock = threading.Lock()

def ai_cevap(messages):

```
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

# Aynı anda başka bir istek varsa beklet.
with gemini_lock:

    max_retries = 3

    for attempt in range(max_retries):

        try:
            response = requests.post(
                url,
```
