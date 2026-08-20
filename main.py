import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()

# Client'i "gecici hatada otomatik, ama SINIRLI sekilde tekrar dene" diye kuruyoruz:
#  - timeout=20000ms -> tek bir istek en fazla 20 sn beklesin, sonsuza kadar takilmasin
#  - attempts=3      -> 503/429 gelirse en fazla 3 kez dene (aralar: 1sn, 2sn)
# Boylece yogunlukta bile toplam bekleme kisa kalir, ekran dakikalarca donmaz.
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(
        timeout=20_000,
        retry_options=types.HttpRetryOptions(
            attempts=3,
            initial_delay=1.0,
            max_delay=4.0,
            exp_base=2.0,
            # Sadece sunucu kaynakli GECICI hatalarda tekrar dene (bunlar birkac sn'de gecer).
            # 429 (kota) BILEREK yok: kota 1-2 sn'de sifirlanmaz, tekrar denemek bosuna bekletir;
            # onun yerine dogrudan yedek modele ve cache'e dusmesi daha hizli/guvenli.
            http_status_codes=[500, 502, 503, 504],
        ),
    ),
)

# Ana model yogunsa sirayla bu yedeklere dusecegiz (ikisi de key'imizle calisiyor)
MODELLER = ["gemini-flash-latest", "gemini-3.6-flash"]

# Son basarili sonucu buraya kaydedecegiz; her sey coker se demo bunu gosterir
CACHE = Path(__file__).with_name("son_basarili_ozet.json")


# 1. Şablonumuz (Formumuz)
class RaporOzeti(BaseModel):
    sirket_adi: str
    hisse_kodu: str
    genel_tavsiye: str
    hedef_fiyat: float


# 2. Uydurma bir borsa raporu metni
rapor_metni = "Bugün yaptığımız analizlerde Aselsan şirketinin (ASELS) oldukça güçlü bir çeyrek geçirdiğini gördük. Yatırımcılara tavsiyemiz AL yönündedir. Yıl sonu için beklediğimiz hisse fiyatı ise 75.50 TL seviyesindedir."


# 3. Sirayla modelleri dene; olmazsa son basarili sonuca (cache) dus
def rapor_ozetle(metin: str) -> str:
    son_hata = None
    for model in MODELLER:
        try:
            cevap = client.models.generate_content(
                model=model,
                contents=metin,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json",  # JSON formatinda cevap iste
                    response_schema=RaporOzeti,             # Doldurulacak form
                ),
            )
            CACHE.write_text(cevap.text, encoding="utf-8")  # basariliysa sakla
            return cevap.text
        except Exception as e:
            son_hata = e
            print(f"[uyari] '{model}' su an cevap vermedi ({type(e).__name__}), yedege geciliyor...")

    # Hicbir model olmadi -> son basarili sonucu goster ki demo cokmesin
    if CACHE.exists():
        print("[bilgi] API su an ulasilamiyor, son basarili sonuc gosteriliyor:")
        return CACHE.read_text(encoding="utf-8")

    raise RuntimeError("Modeller yanit vermiyor ve elde onbellek de yok.") from son_hata


# 4. Cagir ve sonucu ekrana yazdir
print(rapor_ozetle(rapor_metni))
    