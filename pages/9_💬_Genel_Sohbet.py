"""
Genel finans sohbeti (Hafta 2'de yaptigimiz chatbot).
Artik ortak motoru (core/llm.py) kullaniyor.
NOT: Bu arac genel bilgi icindir; belgeye dayali/kaynakli cevap icin
KAP Rapor Zekasi veya Okuryazarlik Asistani araclarini kullan.
"""

import streamlit as st
from core.llm import cevap_akisi, GROQ_MODELLERI

st.set_page_config(page_title="Genel Sohbet", page_icon="💬")

st.title("💬 Genel Finans Sohbeti")
st.caption("Groq (ana) + Gemini (yedek) · streaming + sohbet geçmişi")

st.info(
    "ℹ️ Bu araç modelin genel bilgisini kullanır, **belgeye dayanmaz** — "
    "rakamlar uydurma olabilir (halüsinasyon). Kaynaklı cevap için "
    "belge yükleyen araçları kullan.",
    icon="⚠️",
)

with st.sidebar:
    st.header("⚙️ Ayarlar")
    system_prompt = st.text_area(
        "System prompt (modelin 'iş tanımı')",
        value="Sen Borsa Istanbul odakli, sade ve net konusan bir finans asistanisin. "
              "Emin olmadigin rakamlari UYDURMA; bilmiyorsan bilmedigini soyle.",
        height=140,
    )
    temperature = st.slider("Temperature", 0.0, 2.0, 0.3, 0.1)
    groq_model = st.selectbox("Ana model (Groq)", GROQ_MODELLERI)
    if st.button("🗑️ Sohbeti temizle"):
        st.session_state.sohbet = []
        st.rerun()

if "sohbet" not in st.session_state:
    st.session_state.sohbet = []

for m in st.session_state.sohbet:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if soru := st.chat_input("Bir şey sor..."):
    st.session_state.sohbet.append({"role": "user", "content": soru})
    with st.chat_message("user"):
        st.markdown(soru)
    with st.chat_message("assistant"):
        tam = st.write_stream(
            cevap_akisi(st.session_state.sohbet, system_prompt, temperature, groq_model)
        )
        st.session_state.sohbet.append({"role": "assistant", "content": tam})

st.page_link("app.py", label="← Ana sayfaya dön")
