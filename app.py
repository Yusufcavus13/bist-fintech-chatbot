"""
FinKalkan - Turkiye Gundeminden Fintech Problem Cozucu Platform
================================================================
AMAC: Chatbot yapmak degil, GERCEK SORUNLARI cozmek.
Kullanici derdine gore arac secer; her arac ayni motorlari (LLM + RAG) paylasir.

Bu dosya ANA SAYFA (problem menusu). Her arac 'pages/' altinda ayri sayfa.
"""

import streamlit as st

st.set_page_config(page_title="FinKalkan", page_icon="🛡️", layout="wide")

# --- Baslik ----------------------------------------------------------------
st.title("🛡️ FinKalkan")
st.markdown(
    "**Türkiye'nin güncel finans dertlerine tek platform.** "
    "Derdini seç, aracı kullan — her araç yapay zekâ + gerçek belge/veri ile çalışır."
)

st.info(
    "📌 **Gündem (2026):** Enflasyon ~%25 · Dolar yıl sonu ~50 TL beklentisi · "
    "Dijital dolandırıcılık ve kara para aklama vakaları artışta · "
    "Tasarruf ve finansal okuryazarlık düşük.",
    icon="📊",
)

st.divider()

# --- Arac katalogu ---------------------------------------------------------
# durum: "hazir" | "yapiliyor" | "planlandi"
ARACLAR = [
    {
        "no": 5, "ikon": "📄", "ad": "KAP Rapor Zekâsı",
        "ozet": "200 sayfalık faaliyet raporu → 1 sayfalık yatırımcı özeti, risk radarı ve **kaynak gösteren** soru-cevap.",
        "kim": "Bireysel yatırımcı", "girdi": "KAP faaliyet raporu (PDF)",
        "durum": "yapiliyor", "sayfa": "pages/1_📄_KAP_Rapor_Zekasi.py",
    },
    {
        "no": 4, "ikon": "🔤", "ad": "Finansal Okuryazarlık Asistanı",
        "ozet": "Ağır dilli ürün dokümanını (fon bilgi formu, izahname) sade Türkçeye çevirir, sorularını belgeye dayanarak yanıtlar.",
        "kim": "Ürünü anlamayan vatandaş", "girdi": "Ürün dokümanı (PDF)",
        "durum": "yapiliyor", "sayfa": "pages/2_🔤_Okuryazarlik_Asistani.py",
    },
    {
        "no": 1, "ikon": "🎣", "ad": "Dolandırıcılık Kalkanı",
        "ozet": "Şüpheli mesajı yapıştır → risk skoru, kırmızı bayraklar (garanti getiri, aciliyet, IBAN isteme) ve ne yapman gerektiği.",
        "kim": "Herkes", "girdi": "Şüpheli mesaj/ilan metni",
        "durum": "planlandi", "sayfa": None,
    },
    {
        "no": 3, "ikon": "📉", "ad": "Enflasyon Koçu",
        "ozet": "Harcama ekstreni yükle → nereye para kaçtığını gör, enflasyona karşı kişisel tasarruf planı al.",
        "kim": "Alım gücü eriyen herkes", "girdi": "Ekstre (CSV)",
        "durum": "planlandi", "sayfa": None,
    },
    {
        "no": 2, "ikon": "🕵️", "ad": "AML Erken Uyarı",
        "ozet": "İşlem verisinde aklama tipolojilerini yakalar, şüphelileri risk skoruyla sıralar, otomatik SAR rapor taslağı yazar.",
        "kim": "Uyum (compliance) ekipleri", "girdi": "İşlem verisi (CSV)",
        "durum": "planlandi", "sayfa": None,
    },
    {
        "no": 6, "ikon": "🏭", "ad": "KOBİ Kur & Nakit Akışı Uyarısı",
        "ozet": "Kur hareketleri ve nakit akışını izleyip KOBİ'ye erken uyarı verir.",
        "kim": "KOBİ sahibi", "girdi": "Nakit akışı + kur verisi",
        "durum": "planlandi", "sayfa": None,
    },
    {
        "no": 7, "ikon": "🏦", "ad": "Alternatif Kredi Risk Özeti",
        "ozet": "Finansal tablolardan kredi riski özeti çıkarır.",
        "kim": "Kredi analisti", "girdi": "Finansal tablo",
        "durum": "planlandi", "sayfa": None,
    },
]

ROZET = {
    "hazir": ("✅ Hazır", "normal"),
    "yapiliyor": ("🔨 Yapım aşamasında", "normal"),
    "planlandi": ("📋 Planlandı", "off"),
}

st.subheader("Derdini seç 👇")

# Kartlari 2'li satirlar halinde diz
for i in range(0, len(ARACLAR), 2):
    kolonlar = st.columns(2)
    for kolon, arac in zip(kolonlar, ARACLAR[i:i + 2]):
        with kolon:
            with st.container(border=True):
                etiket, _ = ROZET[arac["durum"]]
                st.markdown(f"### {arac['ikon']} {arac['ad']}")
                st.caption(f"Problem #{arac['no']} · {etiket}")
                st.write(arac["ozet"])
                st.caption(f"👤 **Kime:** {arac['kim']}  \n📥 **Girdi:** {arac['girdi']}")

                if arac["durum"] == "planlandi":
                    st.button("Yakında", key=f"btn{arac['no']}", disabled=True,
                              use_container_width=True)
                else:
                    st.page_link(arac["sayfa"], label="Aracı aç →",
                                 use_container_width=True)

st.divider()
st.caption(
    "FinKalkan · Borsa İstanbul Fintech Hackathon hazırlığı · "
    "Problemler: Türkiye Gündeminden Fintech Problem Bankası"
)
