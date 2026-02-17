"""
2 Ajanlı CrewAI Toplantı Asistanı (RAG destekli)
- Analist: Toplantı metninden kararları çıkarır; girdi dilini(TR/EN) koruyarak çıktıyı da aynı dilde verir.
- Yazıcı: Kararları JIRA görev formatına dönüştürür; girdi dilini(TR/EN) koruyarak çıktıyı da aynı dilde verir.
Ollama llama3:latest (LLM) + nomic-embed-text (RAG embedding) kullanır.
"""

import os
from pathlib import Path

from torch.cuda import temperature

# CrewAI bazen OpenAI key arar; Ollama kullanırken bypass için dummy key
os.environ["OPENAI_API_KEY"] = "sk-111111111111111111111111111111111111111111111111"

from crewai import Agent, Task, Crew, LLM  # pyright: ignore[reportMissingImports]
from crewai_tools import RagTool  # pyright: ignore[reportMissingImports]
from crewai_tools.tools.rag.types import RagToolConfig  # pyright: ignore[reportMissingImports]

# Yerel Ollama LLM
local_llm = LLM(
    model="ollama/llama3:latest",
    base_url="http://localhost:11434",
    temperature=0.2
)

# --- RAG: Yerel bilgi tabanı (Ollama embedding) ---
# CrewAI 1.9.x: Ollama resmen desteklenir; config anahtarı model_name (ollama/types.py).
# Gerekirse: ollama pull nomic-embed-text
_rag_config: RagToolConfig = {
    "embedding_model": {
        "provider": "ollama",
        "config": {
            "model_name": "nomic-embed-text",  # OllamaProviderConfig.model_name
            "url": "http://localhost:11434/api/embeddings",
        },
    },
}
rag_tool = RagTool(config=_rag_config)
# Proje içindeki bilgi tabanı klasörünü ekle
_bilgi_tabani = Path(__file__).resolve().parent / "bilgi_tabani"
if _bilgi_tabani.exists():
    rag_tool.add(data_type="directory", path=str(_bilgi_tabani))

def analiz_et(metin: str):
    """
    Toplantı metnini analiz eder: kararları çıkarır, JIRA görevlerine dönüştürür.
    Girdi dili neyse, çıktı dili de o olur.
    metin: Toplantı notu / transkript metni.
    return: Analiz ve JIRA görevleri çıktısı (string).
    """
    # --- Ajan 1: Analist (RAG ile) ---
    analist = Agent(
        role="Toplantı Analisti",
        goal="Toplantı metinlerini inceleyip alınan kararları net ve maddeler halinde çıkarmak; gerektiğinde bilgi tabanında benzer karar veya kuralları ara.",
        backstory="""Sen deneyimli bir toplantı notu analistisin. 
        EN ÖNEMLİ KURALIN: Girdi metni hangi dildeyse (Türkçe ise Türkçe, İngilizce ise İngilizce), 
        analizini de o dilde yapmalısın. Çeviri yapma, sadece metnin dilini kullanarak kararları özetle.""",
        llm=local_llm,
        tools=[rag_tool],
        verbose=True,
        allow_delegation=False,
    )

    # --- Ajan 2: Yazıcı (JIRA formatı) ---
    yazici = Agent(
        role="JIRA Görev Yazıcı",
        goal="Verilen karar listesini JIRA'ya uygun görev başlığı ve açıklama formatına dönüştürmek.",
        backstory="Sen JIRA kullanımında uzmansın. Her karar için net başlık, açıklama ve gerekirse kabul kriterleri yazarsın.",
        llm=local_llm,
        verbose=True,
        allow_delegation=False,
    )

    # --- Görev 1: Kararları çıkar (RAG: benzer karar/kural ara) ---
    gorev_kararlari_cikar = Task(
        description=f"""Aşağıdaki toplantı metnini oku ve alınan tüm kararları, taahhütleri ve aksiyonları maddeler halinde çıkar.
Her madde kısa ve net olsun. Kim/ne zaman biliniyorsa belirt.
İstersen bilgi tabanında (RAG) benzer karar örnekleri veya JIRA kurallarına bakarak tutarlılık sağla.

ÖNEMLİ: Toplantı metni hangi dilde yazılmışsa (Türkçe, İngilizce vb.) çıktını da AYNI DİLDE yaz. Metnin dilini koru.
Giriş veya çıkış cümlesi ekleme, sadece maddeleri yaz.

TOPLANTI METNİ:
---
{metin}
---""",
        expected_output="Giriş cümlesi içermeyen,Madde madde, numaralı karar/aksiyon listesi. Her madde tek paragraf. Çıktı mutlaka toplantı metninin dilinde olmalı.",
        agent=analist,
    )

    # --- Görev 2: JIRA görevlerine dönüştür (Analist çıktısını kullan) ---
    gorev_jira_yaz = Task(
        description="""Sana verilen karar listesini JIRA görevleri formatına dönüştür.
Her karar için:
- Başlık: Kısa, aksiyon odaklı (örn. "[Backend] API v2 dokümantasyonunu tamamla")
- Açıklama: 1-2 cümle ile ne yapılacak
- İsteğe bağlı: Kabul kriterleri veya etiket önerisi

Çıktıyı her görev için ayrı blok halinde yaz; JIRA'ya kopyala-yapıştır yapılabilsin.

ÖNEMLİ: Karar listesi hangi dilde verildiyse (Türkçe, İngilizce vb.) JIRA görevlerini de AYNI DİLDE yaz. Başlık ve açıklamalar metnin dilinde olmalı.""",
        expected_output="Her biri başlık + açıklama içeren JIRA görevleri listesi. Çıktı mutlaka karar listesinin dilinde olmalı.",
        agent=yazici,
        context=[gorev_kararlari_cikar],
    )

    # --- Crew: 2 ajan, sıralı 2 görev ---
    ekip = Crew(
        agents=[analist, yazici],
        tasks=[gorev_kararlari_cikar, gorev_jira_yaz],
    )

    sonuc = ekip.kickoff()
    return sonuc


# Örnek toplantı metni (doğrudan çalıştırıldığında kullanılır)
TOPLANTI_METNI = """
Sprint 42 Planlama Toplantısı - 14 Şubat 2025

Katılımcılar: Ahmet, Ayşe, Mehmet, Zeynep

Gündem:
1. Yeni ödeme entegrasyonu tamamlandı. Bir sonraki sprintte production'a alınacak.
2. Kullanıcı şikayetleri: mobil uygulama yavaş. Performans ekibi öncelik verecek.
3. API v2 dokümantasyonu eksik. Backend ekibi 2 hafta içinde tamamlayacak.
4. Yıllık bakım penceresi 1 Mart'ta 02:00-06:00 arası yapılacak.
5. Yeni stajyer onboarding dokümanı hazırlanacak; İK ile koordinasyon kararlaştırıldı.
"""

if __name__ == "__main__":
    print("\n### Toplantı Asistanı - Analiz ve JIRA Görevleri ###\n")
    sonuc = analiz_et(TOPLANTI_METNI)
    print("\n--- Sonuç ---\n")
    print(sonuc)
