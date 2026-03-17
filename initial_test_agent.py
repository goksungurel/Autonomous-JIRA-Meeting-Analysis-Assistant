import os
from crewai import Agent, Task, Crew, LLM  # pyright: ignore[reportMissingImports]

# 1. Bypass OpenAI API key requirement
os.environ["OPENAI_API_KEY"] = "sk-111111111111111111111111111111111111111111111111"

# 2. Local LLM Configuration - Using the exact model name from Ollama
local_llm = LLM(
    model="ollama/llama3:latest",
    base_url="http://localhost:11434"
)

# 3. Agent Definition
ai_mentor = Agent(
    role='AI Mentor',
    goal='Congratulate the software engineering student for successfully running a local AI on their MacBook Air.',
    backstory='You are the most experienced and encouraging AI instructor in the world. You appreciate clean code and local deployments.',
    llm=local_llm,
    verbose=True,
    allow_delegation=False
)

# 4. Task Definition
celebration_task = Task(
    description="We successfully deployed and ran a local LLM environment on a MacBook Air without relying on external APIs. Write a very short, highly enthusiastic congratulatory message.",
    expected_output="A single, highly motivating and professional congratulatory sentence.",
    agent=ai_mentor
)

# 5. Assemble and Run the Crew
test_crew = Crew(
    agents=[ai_mentor], 
    tasks=[celebration_task]
)

print("\n### Initializing AI Analysis... ###\n")
print(test_crew.kickoff())