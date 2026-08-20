"""
Ortak LLM motoru - tum araclar bunu kullanir.
Groq (ANA, cok hizli) + Gemini (YEDEK). Groq calisirken Gemini'ye hic dokunulmaz.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from google import genai
from google.genai import types

load_dotenv()

GROQ_MODELLERI = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]
GEMINI_MODEL = "gemini-flash-latest"

# Modele HTML degil Markdown yazdirmak icin (yoksa cevapta <ul><li> gorunur)
BICIM_TALIMATI = (
    "\n\nBICIM KURALI: Cevabini SADECE Markdown ile bicimlendir. "
    "HTML etiketi (<ul>, <li>, <p>, <b>, <table> vb.) ASLA kullanma. "
    "Liste icin '- ' ile madde yaz, vurgu icin **...** kullan."
)


def anahtar_al(isim):
    """Anahtari once bulut (st.secrets), sonra yerel (.env) icinde ara."""
    try:
        if isim in st.secrets:
            return st.secrets[isim]
    except Exception:
        pass
    return os.getenv(isim)


@st.cache_resource
def groq_client():
    return Groq(api_key=anahtar_al("GROQ_API_KEY"))


@st.cache_resource
def gemini_client():
    return genai.Client(
        api_key=anahtar_al("GEMINI_API_KEY"),
        http_options=types.HttpOptions(
            timeout=30_000,
            retry_options=types.HttpRetryOptions(
                attempts=2, initial_delay=1.0, max_delay=4.0,
                http_status_codes=[500, 502, 503, 504],
            ),
        ),
    )


def _gemini_contents(mesajlar):
    """Bizim mesaj formatini Gemini'nin bekledigi formata cevirir."""
    out = []
    for m in mesajlar:
        rol = "user" if m["role"] == "user" else "model"
        out.append(types.Content(role=rol, parts=[types.Part(text=m["content"])]))
    return out


def cevap_akisi(mesajlar, system_prompt, temperature=0.3, groq_model=GROQ_MODELLERI[0]):
    """
    Streaming cevap uretir (generator).
    Once Groq'a sorar; herhangi bir hata olursa sessizce Gemini'ye duser.
    """
    sistem = system_prompt + BICIM_TALIMATI

    # 1) ANA: Groq
    try:
        stream = groq_client().chat.completions.create(
            model=groq_model,
            messages=[{"role": "system", "content": sistem}] + mesajlar,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            parca = chunk.choices[0].delta.content
            if parca:
                yield parca
        return
    except Exception:
        pass

    # 2) YEDEK: Gemini
    try:
        stream = gemini_client().models.generate_content_stream(
            model=GEMINI_MODEL,
            contents=_gemini_contents(mesajlar),
            config=types.GenerateContentConfig(
                system_instruction=sistem, temperature=temperature,
            ),
        )
        for chunk in stream:
            if chunk.text:
                yield chunk.text
        return
    except Exception:
        yield "⚠️ Su an iki servis de yanit veremedi. Birkac saniye sonra tekrar dene."


def cevap_tam(mesajlar, system_prompt, temperature=0.3):
    """Streaming olmadan tam metin dondurur (arka plan islerinde kullanilir)."""
    return "".join(cevap_akisi(mesajlar, system_prompt, temperature))
