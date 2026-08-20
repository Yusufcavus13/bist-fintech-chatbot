"""Hafta 1 - son madde: STREAMING (akan cikti).
Normal cagrida cevabin tamami gelene kadar beklersin.
Streaming'de cevap ChatGPT gibi parca parca (chunk) akar -> kullaniciya daha canli hissettirir.
Tek fark: generate_content YERINE generate_content_stream + for dongusu."""

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

soru = "Bana 3 cumleyle RAG (Retrieval-Augmented Generation) nedir anlat."

print("Soru:", soru)
print("Cevap: ", end="", flush=True)

# generate_content_stream bir "generator" dondurur -> parca parca gelir.
# (Algoritma gecmisin varsa: bu bir iterator, her adimda bir chunk uretir.)
for chunk in client.models.generate_content_stream(
    model="gemini-flash-latest",
    contents=soru,
):
    if chunk.text:
        print(chunk.text, end="", flush=True)  # aninda ekrana yaz, satir atlamadan

print()  # en sona bir satir atla
