"""
2 Ajanlı CrewAI Toplantı Asistanı
- Analist: Toplantı metninden kararları çıkarır
- Yazıcı: Kararları JIRA görev formatına dönüştürür
Ollama llama3:latest kullanır.
"""

import os

# CrewAI bazen OpenAI key arar; Ollama kullanırken bypass için dummy key
os.environ["OPENAI_API_KEY"] = "sk-111111111111111111111111111111111111111111111111"

from crewai import Agent, Task, Crew, LLM  # pyright: ignore[reportMissingImports]

# Yerel Ollama LLM
local_llm = LLM(
    model="ollama/llama3:latest",
    base_url="http://localhost:11434",
)

# Örnek toplantı metni (istediğin metinle değiştirebilirsin)
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

# --- Ajan 1: Analist ---
analist = Agent(
    role="Toplantı Analisti",
    goal="Toplantı metinlerini inceleyip alınan kararları net ve maddeler halinde çıkarmak.",
    backstory="Sen deneyimli bir toplantı notu analistisin. Metinlerdeki karar, taahhüt ve aksiyonları ayırt edersin.",
    llm=local_llm,
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

# --- Görev 1: Kararları çıkar ---
gorev_kararlari_cikar = Task(
    description=f"""Aşağıdaki toplantı metnini oku ve alınan tüm kararları, taahhütleri ve aksiyonları maddeler halinde çıkar.
Her madde kısa ve net olsun. Kim/ne zaman biliniyorsa belirt.

TOPLANTI METNİ:
---
{TOPLANTI_METNI}
---""",
    expected_output="Madde madde, numaralı karar/aksiyon listesi. Her madde tek paragraf.",
    agent=analist,
)

# --- Görev 2: JIRA görevlerine dönüştür (Analist çıktısını kullan) ---
gorev_jira_yaz = Task(
    description="""Sana verilen karar listesini JIRA görevleri formatına dönüştür.
Her karar için:
- Başlık: Kısa, aksiyon odaklı (örn. "[Backend] API v2 dokümantasyonunu tamamla")
- Açıklama: 1-2 cümle ile ne yapılacak
- İsteğe bağlı: Kabul kriterleri veya etiket önerisi

Çıktıyı her görev için ayrı blok halinde yaz; JIRA'ya kopyala-yapıştır yapılabilsin.""",
    expected_output="Her biri başlık + açıklama içeren JIRA görevleri listesi.",
    agent=yazici,
    context=[gorev_kararlari_cikar],
)

# --- Crew: 2 ajan, sıralı 2 görev ---
ekip = Crew(
    agents=[analist, yazici],
    tasks=[gorev_kararlari_cikar, gorev_jira_yaz],
)

if __name__ == "__main__":
    print("\n### Toplantı Asistanı - Analiz ve JIRA Görevleri ###\n")
    sonuc = ekip.kickoff()
    print("\n--- Sonuç ---\n")
    print(sonuc)
