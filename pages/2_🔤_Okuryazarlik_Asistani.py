"""
Problem #4 - Finansal Okuryazarlik Asistani
Agir dilli urun dokumanini sade Turkce'ye cevirir, belgeye dayali cevap verir.
Hafta 3'te ayni RAG motorunu kullanacak.
"""

import streamlit as st

st.set_page_config(page_title="Okuryazarlık Asistanı", page_icon="🔤", layout="wide")

st.title("🔤 Finansal Okuryazarlık Asistanı")
st.caption("Problem #4 · Ürün dokümanları ağır dille yazılı, kimse okumuyor")

st.warning(
    "🔨 **Yapım aşamasında** — Hafta 3'te RAG motoru bağlanacak.",
    icon="🔨",
)

st.subheader("Hedeflenen akış")
st.markdown(
    """
1. **Doküman yükle** — fon bilgi formu, izahname, ürün dokümanı (PDF)
2. **Sade dille sor** — "Bu fon riskli mi? Param ne kadar bağlı kalır?"
3. **Lise seviyesinde cevap** — jargon açıklanır, karmaşık ifade sadeleştirilir
4. **Kaynak gösterimi** — cevabın belgenin neresinden geldiği belirtilir
"""
)

st.file_uploader("Ürün dokümanı (PDF)", type="pdf", disabled=True,
                 help="Hafta 3'te aktifleşecek")

st.page_link("app.py", label="← Ana sayfaya dön")
