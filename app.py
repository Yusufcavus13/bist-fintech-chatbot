"""
Hafta 2 - Streamlit Chatbot (Gemini destekli)
----------------------------------------------
ONEMLI KAVRAM: Streamlit, sen her sey yaptiginda (mesaj yazma, buton, slider)
bu dosyayi BASTAN ASAGI yeniden calistirir. Yani script tekrar tekrar kosar.
Bu yuzden "hatirlanmasi gereken" seyleri (sohbet gecmisi gibi) normal degiskende
tutamayiz -> her calismada sifirlanir. Onun yerine 'st.session_state' kullaniriz;
o, yeniden calismalar arasinda YASAR (kalici hafiza gibi dusun).
"""

import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# --- API anahtarini akilli bul: hem yerelde hem bulutta calissin -----------
# Deploy edilince (Streamlit Cloud) anahtar 'st.secrets'ten gelir.
# Yerelde (senin bilgisayarin) ise .env'den gelir. Ikisini de destekle:
def api_key_al():
    try:
        if "GEMINI_API_KEY" in st.secrets:      # Streamlit Cloud "Secrets" kutusu
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass                                    # yerelde secrets.toml yoksa sorun degil
    return os.getenv("GEMINI_API_KEY")          # .env'e dus

# --- 1) Client'i bir kez kur ve sakla ---------------------------------------
# @st.cache_resource: her yeniden calismada client'i SIFIRDAN yaratma, bir kez
# yaratip sakla (pahali nesneler icin). C#'ta 'singleton' gibi dusunebilirsin.
@st.cache_resource
def client_al():
    return genai.Client(
        api_key=api_key_al(),
        http_options=types.HttpOptions(
            timeout=20_000,
            retry_options=types.HttpRetryOptions(
                attempts=3, initial_delay=1.0, max_delay=4.0,
                http_status_codes=[500, 502, 503, 504],  # 429 (kota) haric
            ),
        ),
    )

client = client_al()

# --- 2) Sayfa ayarlari + baslik ---------------------------------------------
st.set_page_config(page_title="Fintech Asistani", page_icon="📈")
st.title("📈 Fintech Chatbot")
st.caption("Hafta 2 · Streamlit + Gemini · streaming + sohbet gecmisi")

# --- 3) Kenar cubugu (sidebar): davranisi CANLI degistir --------------------
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

    model_adi = st.selectbox(
        "Model",
        ["gemini-flash-latest", "gemini-3.6-flash"],
    )

    if st.button("🗑️ Sohbeti temizle"):
        st.session_state.messages = []
        st.rerun()  # ekrani hemen yenile

# --- 4) Sohbet gecmisini kalici hafizada baslat -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []   # her eleman: {"role": "user"/"assistant", "content": "..."}

# --- 5) Simdiye kadarki gecmisi ekrana ciz ----------------------------------
for mesaj in st.session_state.messages:
    with st.chat_message(mesaj["role"]):        # baloncuk (user / assistant)
        st.markdown(mesaj["content"])

# --- Yardimci: bizim gecmisi Gemini'nin bekledigi formata cevir -------------
# Not: Gemini AI tarafina "assistant" degil "model" der.
def gecmisi_contents_yap(messages):
    contents = []
    for m in messages:
        rol = "user" if m["role"] == "user" else "model"
        contents.append(types.Content(role=rol, parts=[types.Part(text=m["content"])]))
    return contents

# --- 6) Kullanicidan girdi al (en alttaki sohbet kutusu) --------------------
if soru := st.chat_input("Bir sey sor... (or: Aselsan hakkinda kisa bilgi ver)"):
    # a) kullanici mesajini gecmise ekle + ekrana bas
    st.session_state.messages.append({"role": "user", "content": soru})
    with st.chat_message("user"):
        st.markdown(soru)

    # b) modelin cevabini STREAMING ile bas
    with st.chat_message("assistant"):
        try:
            stream = client.models.generate_content_stream(
                model=model_adi,
                contents=gecmisi_contents_yap(st.session_state.messages),
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,   # sidebar'daki is tanimi
                    temperature=temperature,             # sidebar'daki slider
                ),
            )

            # st.write_stream, generator'dan gelen parcalari canli akitir
            # ve sonunda tam metni dondurur.
            def metin_akisi():
                for chunk in stream:
                    if chunk.text:
                        yield chunk.text

            tam_cevap = st.write_stream(metin_akisi)

            # c) modelin cevabini da gecmise ekle (ki sonraki turda hatirlasin)
            st.session_state.messages.append({"role": "assistant", "content": tam_cevap})

        except Exception as e:
            # Cokme yerine kullaniciya nazik hata goster (or: 429 kota, 503 yogunluk)
            st.error(f"Su an cevap alinamadi: {type(e).__name__}. "
                     f"Kota dolduysa ~1 dk sonra tekrar dene.")
