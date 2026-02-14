import os
from crewai import Agent, Task, Crew, LLM  # pyright: ignore[reportMissingImports]

# 1. OpenAI kontrolünü bypass et
os.environ["OPENAI_API_KEY"] = "sk-111111111111111111111111111111111111111111111111"

# 2. Yerel LLM Yapılandırması - Tam olarak terminaldeki ismi yazdık
local_llm = LLM(
    model="ollama/llama3:latest",
    base_url="http://localhost:11434"
)

# 3. Ajan Tanımı
mentor = Agent(
    role='AI Mentor',
    goal='MacBook Air üzerinde yerel AI çalıştırmayı başaran öğrenciyi tebrik etmek.',
    backstory='Sen dünyanın en tecrübeli AI eğitmenisin.',
    llm=local_llm,
    verbose=True,
    allow_delegation=False
)

# 4. Görev Tanımı
gorev = Task(
    description="MacBook Air üzerinde yerel AI çalıştırmayı başardık. Çok kısa ve heyecanlı bir tebrik mesajı yaz.",
    expected_output="Motive edici tek bir cümle.",
    agent=mentor
)

# 5. Ekibi Kur ve Çalıştır
ekip = Crew(agents=[mentor], tasks=[gorev])

print("\n### AI Analize Başlıyor... ###\n")
print(ekip.kickoff())