"""
Hafta 2 - Streamlit Chatbot (Groq ANA + Gemini YEDEK)
------------------------------------------------------
ONEMLI KAVRAM: Streamlit, sen her sey yaptiginda (mesaj, buton, slider)
bu dosyayi BASTAN ASAGI yeniden calistirir. Bu yuzden hatirlanmasi gereken
seyleri (sohbet gecmisi) 'st.session_state' icinde tutariz; o, yeniden
calismalar arasinda YASAR.

DAYANIKLILIK: Once Groq'a soruyoruz (cok hizli, yuksek limit). Groq bir sebeple
cevap vermezse OTOMATIK Gemini'ye dusuyoruz. Boylece kullanici hata gormez.
Normalde sadece Groq calisir -> yavaslamaz.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from google import genai
from google.genai import types

load_dotenv()

GROQ_MODEL_SECENEKLERI = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]  # ana (hizli)
GEMINI_MODEL = "gemini-flash-latest"                                    # yedek

# Modele HTML degil Markdown yazdirmak icin (yoksa cevapta <ul><li> gorunur).
# Bu kural, sidebar'daki system prompt ne olursa olsun HEP eklenir.
BICIM_TALIMATI = (
    "\n\nBICIM KURALI: Cevabini SADECE Markdown ile bicimlendir. "
    "HTML etiketi (<ul>, <li>, <p>, <b>, <table> vb.) ASLA kullanma. "
    "Liste icin '- ' ile madde yaz, vurgu icin **...** kullan."
)


# --- API anahtarlarini akilli bul: hem yerel (.env) hem bulut (st.secrets) --
def anahtar_al(isim):
    try:
        if isim in st.secrets:          # Streamlit Cloud "Secrets"
            return st.secrets[isim]
    except Exception:
        pass                            # yerelde secrets.toml yoksa sorun degil
    return os.getenv(isim)              # .env'e dus


# --- Client'leri bir kez kur ve sakla (singleton) --------------------------
@st.cache_resource
def groq_client_al():
    return Groq(api_key=anahtar_al("GROQ_API_KEY"))

@st.cache_resource
def gemini_client_al():
    return genai.Client(
        api_key=anahtar_al("GEMINI_API_KEY"),
        http_options=types.HttpOptions(
            timeout=30_000,   # yedek cabuk pes etsin diye kisa tutuldu
            retry_options=types.HttpRetryOptions(
                attempts=2, initial_delay=1.0, max_delay=4.0,
                http_status_codes=[500, 502, 503, 504],
            ),
        ),
    )

groq_client = groq_client_al()
gemini_client = gemini_client_al()


# --- Sayfa ayarlari + baslik ------------------------------------------------
st.set_page_config(page_title="Fintech Asistani", page_icon="📈")
st.title("📈 Fintech Chatbot")
st.caption("Hafta 2 · Groq (ana) + Gemini (yedek) · streaming + sohbet gecmisi")


# --- Kenar cubugu: davranisi CANLI degistir ---------------------------------
with st.sidebar:
    st.header("⚙️ Ayarlar")

    system_prompt = st.text_area(
        "System prompt (modelin 'is tanimi')",
        value="Sen Borsa Istanbul odakli, sade ve net konusan bir finans asistanisin. "
              "Emin olmadigin rakamlari UYDURMA; bilmiyorsan bilmedigini soyle.",
        height=140,
        help="Bunu degistirip ayni soruyu tekrar sor -> davranisin nasil degistigini gor.",
    )

    temperature = st.slider(
        "Temperature (0 = net/kararli, yuksek = yaratici)",
        min_value=0.0, max_value=2.0, value=0.3, step=0.1,
    )

    groq_model = st.selectbox(
        "Ana model (Groq)",
        GROQ_MODEL_SECENEKLERI,
        help="120b daha guclu, 20b daha hizli. Ikisi de cok hizli.",
    )

    if st.button("🗑️ Sohbeti temizle"):
        st.session_state.messages = []
        st.rerun()


# --- Sohbet gecmisini kalici hafizada baslat --------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []   # her eleman: {"role": "user"/"assistant", "content": "..."}

# --- Simdiye kadarki gecmisi ekrana ciz -------------------------------------
for mesaj in st.session_state.messages:
    with st.chat_message(mesaj["role"]):
        st.markdown(mesaj["content"])


# --- Yardimci: bizim gecmisi Gemini'nin formatina cevir ---------------------
def gemini_contents_yap(mesajlar):
    out = []
    for m in mesajlar:
        rol = "user" if m["role"] == "user" else "model"   # Gemini "assistant" degil "model" der
        out.append(types.Content(role=rol, parts=[types.Part(text=m["content"])]))
    return out


# --- KALP: once Groq, cokerse Gemini. Ikisi de streaming. -------------------
def cevap_akisi(mesajlar, system_prompt, temperature, groq_model):
    sistem = system_prompt + BICIM_TALIMATI   # HTML yerine Markdown zorla
    # 1) ANA: Groq (hizli, yuksek limit)
    try:
        stream = groq_client.chat.completions.create(
            model=groq_model,
            messages=[{"role": "system", "content": sistem}] + mesajlar,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            parca = chunk.choices[0].delta.content
            if parca:
                yield parca
        return  # basariyla bitti, Gemini'ye hic dokunma
    except Exception:
        pass    # Groq patladi -> sessizce yedege gec

    # 2) YEDEK: Gemini
    try:
        stream = gemini_client.models.generate_content_stream(
            model=GEMINI_MODEL,
            contents=gemini_contents_yap(mesajlar),
            config=types.GenerateContentConfig(
                system_instruction=sistem,
                temperature=temperature,
            ),
        )
        for chunk in stream:
            if chunk.text:
                yield chunk.text
        return
    except Exception:
        yield "⚠️ Su an iki servis de yanit veremedi. Lutfen birkac saniye sonra tekrar dene."


# --- Kullanicidan girdi al --------------------------------------------------
if soru := st.chat_input("Bir sey sor... (or: Aselsan hakkinda kisa bilgi ver)"):
    st.session_state.messages.append({"role": "user", "content": soru})
    with st.chat_message("user"):
        st.markdown(soru)

    with st.chat_message("assistant"):
        tam_cevap = st.write_stream(
            cevap_akisi(st.session_state.messages, system_prompt, temperature, groq_model)
        )
        st.session_state.messages.append({"role": "assistant", "content": tam_cevap})
