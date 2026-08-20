"""
Problem #5 - KAP Rapor Zekasi
200 sayfalik faaliyet raporu -> ozet + risk radari + kaynakli soru-cevap.
Hafta 3'te RAG motoru buraya baglanacak.
"""

import streamlit as st

st.set_page_config(page_title="KAP Rapor Zekâsı", page_icon="📄", layout="wide")

st.title("📄 KAP Rapor Zekâsı")
st.caption("Problem #5 · Bireysel yatırımcı 200 sayfalık raporu okuyamıyor")

st.warning(
    "🔨 **Yapım aşamasında** — Hafta 3'te RAG motoru bağlanacak. "
    "Aşağıdaki akış hedeflenen ürünü gösteriyor.",
    icon="🔨",
)

st.subheader("Hedeflenen akış")
st.markdown(
    """
1. **Rapor yükle** — KAP faaliyet raporu (PDF)
2. **Otomatik yönetici özeti** — 200 sayfa → 1 sayfa yatırımcı özeti
3. **Risk radarı** — rapordaki risk cümleleri çıkarılıp kategorize edilir (kur riski, borçluluk, dava...)
4. **Kaynaklı soru-cevap** — "net kâr ne kadar?" → cevap **+ hangi sayfadan geldiği**
5. **Halüsinasyon koruması** — sadece belgedeki bilgiyle cevap; bilgi yoksa "belgede yok" der
"""
)

st.file_uploader("KAP faaliyet raporu (PDF)", type="pdf", disabled=True,
                 help="Hafta 3'te aktifleşecek")

st.page_link("app.py", label="← Ana sayfaya dön")
