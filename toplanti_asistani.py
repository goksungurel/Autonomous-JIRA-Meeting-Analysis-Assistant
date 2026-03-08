"""
2 Ajanlı CrewAI Toplantı Asistanı (RAG destekli + Otonom JIRA Entegrasyonu)
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool
from crewai_tools import RagTool
from atlassian import Jira
from pydantic import BaseModel, Field
from typing import Type

# .env yükle
load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

# --- JIRA GÖREV OLUŞTURMA ARACI ---
class JiraTaskSchema(BaseModel):
    summary: str = Field(..., description="JIRA görevinin kısa ve net başlığı.")
    description: str = Field(..., description="JIRA görevinin detaylı açıklaması ve kabul kriterleri.")

# --- JIRA GÖREV OLUŞTURMA ARACI ---

class JiraTaskTool(BaseTool):
    name: str = "JiraTaskCreator"
    description: str = """
    JIRA üzerinde yeni bir görev (task) oluşturur. 
    Bu aracı kullanırken 'Action Input' olarak sadece tek bir JSON objesi göndermelisin. 
    Örnek format:
    {
        "summary": "Görev başlığı buraya gelecek",
        "description": "Görev detayı ve kimin yapacağı buraya gelecek"
    }
    """

    def _run(self, summary: str, description: str) -> str:
        try:
            jira = Jira(
                url=JIRA_URL,
                username=JIRA_EMAIL,
                password=JIRA_TOKEN,
                cloud=True
            )
            
            issue = jira.issue_create(fields={
                'project': {'key': JIRA_PROJECT_KEY},
                'summary': summary,
                'description': description,
                'issuetype': {'name': 'Task'},
            })
            return f"BAŞARILI: {issue['key']} anahtarlı görev JIRA'da oluşturuldu."
        except Exception as e:
            return f"HATA: JIRA görevi oluşturulamadı. Detay: {str(e)}"

# Pydantic schema sınıflarını (JiraTaskSchema) tamamen sildim ve description içine LLM'i yönlendirecek bir prompt ekledim.
jira_tool = JiraTaskTool()

# --- LLM VE RAG AYARLARI ---
os.environ["OPENAI_API_KEY"] = "sk-dummy"

local_llm = LLM(
    model="ollama/llama3:latest",
    base_url="http://localhost:11434",
    temperature=0.2
)

_rag_config = {
    "embedding_model": {
        "provider": "ollama",
        "config": {
            "model_name": "nomic-embed-text",
            "url": "http://localhost:11434/api/embeddings",
        },
    },
}

rag_tool = RagTool(config=_rag_config)
_bilgi_tabani = Path(__file__).resolve().parent / "bilgi_tabani"
if _bilgi_tabani.exists():
    rag_tool.add(data_type="directory", path=str(_bilgi_tabani))

# --- ANALİZ FONKSİYONU ---
def analiz_et(metin: str):
    analist = Agent(
        role="Toplantı Analisti",
        goal="Toplantı metinlerinden aksiyon alınması gereken kararları net ve maddeler halinde çıkarmak.",
        backstory="Sen deneyimli bir IT iş analistisin. Girdi metninin dilini korumalısın.",
        llm=local_llm,
        #tools=[rag_tool],
        verbose=True
    )

    yazici = Agent(
        role="JIRA Operasyon Uzmanı",
        goal="Kararları JiraTaskCreator aracını kullanarak JIRA'da kayıt açmak.",
        backstory="""Sen sadece metin yazan bir asistan değilsin, JIRA sisteminde işlem yapan otonom bir ajansın. 
        Sana verilen her bir karar maddesi için JiraTaskCreator aracını TEK TEK çalıştırmalısın.""",
        llm=local_llm,
        tools=[jira_tool], 
        verbose=True
    )

    gorev_kararlari_cikar = Task(
        description=f"Aşağıdaki toplantı metninden yazılım ekibi için aksiyon maddelerini çıkar:\n\n{metin}",
        expected_output="Giriş cümlesi içermeyen, madde madde teknik karar ve aksiyon listesi.",
        agent=analist,
    )

    gorev_jira_yaz = Task(
        description="""JiraTaskCreator aracını kullanarak oluşturduğun görevlerin sonucunu raporla. 
        Sadece şu formatta yaz:
        ✅ [JIRA_KEY] - Görev Başlığı: Başarıyla oluşturuldu.""",
        expected_output="Oluşturulan görevlerin temiz bir listesi.",
        agent=yazici,
        context=[gorev_kararlari_cikar],
    )

    ekip = Crew(
        agents=[analist, yazici],
        tasks=[gorev_kararlari_cikar, gorev_jira_yaz],
    )

    return ekip.kickoff()