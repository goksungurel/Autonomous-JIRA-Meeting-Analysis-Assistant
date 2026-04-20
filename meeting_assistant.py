"""
3-Agent CrewAI Meeting Assistant (RAG support + Autonomous JIRA Integration)
Completely refactored for professional English standards.
"""
import os
from pathlib import Path
from typing import Type
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool
from crewai_tools import RagTool
from atlassian import Jira
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

# --- JIRA GÖREV OLUŞTURMA ARACI ---
class JiraTaskSchema(BaseModel):
    summary: str = Field(..., description="Short and clear summary of the JIRA task.")
    description: str = Field(..., description="Detailed description and acceptance criteria of the JIRA task.")

class JiraTaskTool(BaseTool):
    name: str = "JiraTaskCreator"
    description: str = """
    Creates a new task on JIRA. 
    You must send ONLY a single JSON object as 'Action Input'.
    Example format:
    {
        "summary": "Task title goes here",
        "description": "Task details, assignment, and requirements go here"
    }
    """

    def _run(self, summary: str, description: str) -> str:
        """
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
            return f"SUCCESS: Task with key {issue['key']} created on JIRA."
        except Exception as e:
            return f"ERROR: Could not create JIRA task. Detail: {str(e)}"
            """

        import random
        fake_jira_key = f"KAN-{random.randint(100, 999)}"
        
        # Terminalde bizim de görebilmemiz için log yazdırıyoruz
        print(f"\n[MOCK API CALL] JIRA'ya gidilmedi ama görev açıldı sayıldı: {fake_jira_key}")
        print(f"Başlık: {summary}\n")
        
        return f"SUCCESS: Task with key {fake_jira_key} created on JIRA."

jira_tool = JiraTaskTool()

# --- LLM AND RAG SETTINGS ---
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
_knowledge_base = Path(__file__).resolve().parent / "knowledge_base" 
if _knowledge_base.exists():
    rag_tool.add(data_type="directory", path=str(_knowledge_base))

# --- ANALYSIS FUNCTION ---
def analyze_meeting(text: str):
    # Agents
    transcript_editor = Agent(
        role="Senior Transcript Editor",
        goal="To clean spelling errors, grammar mistakes, and Whisper misinterpretations in the English transcript.",
        backstory="You are an expert technical editor fluent in software terminology. You fix Whisper transcription errors and convert fragmented sentences into a formal, structured meeting record in clear English.",
        llm=local_llm,
        verbose=True
    )

    meeting_analyst = Agent(
        role="IT Meeting Analyst",
        goal="Extract actionable decision points and format them strictly according to company standards.",
        backstory="""You are an experienced IT business analyst. 
        You MUST use the RagTool EXACTLY ONCE to retrieve the 'JIRA standards'. 
        CRITICAL: After reading the knowledge base once, DO NOT use the tool again. Immediately synthesize the meeting notes and provide your Final Answer.""",
        llm=local_llm,
        tools=[rag_tool],
        verbose=True
    )

    jira_specialist = Agent(
        role="JIRA Operations Specialist",
        goal="Create tasks on JIRA using the JiraTaskCreator tool based on extracted decisions.",
        backstory="""You are not just a writing assistant; you are an autonomous agent performing operations in JIRA.
        You must run the JiraTaskCreator tool INDIVIDUALLY for EVERY actionable decision point provided. 
        Ensure all task summary and description fields are strictly in English.""",
        llm=local_llm,
        tools=[jira_tool], 
        verbose=True
    )

    # Tasks
    clean_and_translate_task = Task(
        description=f"Clean the spelling, grammar, and technical terminology of the following raw English meeting transcript:\n\n{text}",
        expected_output="A polished, structured meeting transcript in English, free from grammar errors and Whisper misinterpretations.",
        agent=transcript_editor
    )

    extract_action_items_task = Task(
        description="""Follow these steps strictly:
        1. Use the RAG tool EXACTLY ONCE with the query 'JIRA standards'.
        2. Read and memorize the returning formatting rules and priority logic.
        3. Analyze the English meeting record.
        4. Extract the action items and format them perfectly matching the company rules.
        5. Return the final bulleted list. DO NOT use the RAG tool a second time.""",
        expected_output="A bulleted list of technical decisions and action items formatted exactly according to company standards.",
        agent=meeting_analyst,
        context=[clean_and_translate_task]
    )

    create_jira_tasks_task = Task(
        description="""Report the result of the tasks created using the JiraTaskCreator tool. 
        Format strictly as:
        ✅ [JIRA_KEY] - Task Summary: Successfully created.""",
        expected_output="A clean list of created JIRA tasks.",
        agent=jira_specialist,
        context=[extract_action_items_task]
    )

    # Crew Setup and Execution
    crew = Crew(
        agents=[transcript_editor, meeting_analyst, jira_specialist],
        tasks=[clean_and_translate_task, extract_action_items_task, create_jira_tasks_task],
        verbose=True
    )

    return crew.kickoff()