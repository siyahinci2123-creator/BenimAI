import requests

def ai_cevap(mesaj):
    response = requests.post(
        "http://127.0.0.1:11434/api/generate",
        json={
            "model": "qwen2.5:3b",
            "prompt": f"""Sen BenimAI adlı bir yapay zekâ asistanısın.
Her zaman Türkçe cevap ver.
Kendini Alibaba Cloud veya başka bir şirketin asistanı olarak tanıtma.
Kullanıcıya yardımcı ve doğal cevaplar ver.

Kullanıcı: {mesaj}
BenimAI:""",
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()
    return response.json()["response"]


print("🤖 BenimAI başlatıldı!")
print("Çıkmak için 'çıkış' yaz.\n")

while True:
    mesaj = input("Sen: ")

    if mesaj.lower() == "çıkış":
        print("BenimAI: Görüşürüz!")
        break

    try:
        cevap = ai_cevap(mesaj)
        print("BenimAI:", cevap)
    except Exception as e:
        print("Hata:", e)