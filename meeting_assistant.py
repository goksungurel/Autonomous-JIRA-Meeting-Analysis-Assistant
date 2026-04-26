"""
3-Agent CrewAI Meeting Assistant (RAG support + Autonomous JIRA Integration)
Completely refactored for professional English standards.
"""
import os
from pathlib import Path
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
def _build_guidance_block(human_input: str) -> str:
    user_guidance = (human_input or "").strip()
    return (
        f"\n\nAdditional human guidance from the user:\n{user_guidance}"
        if user_guidance
        else ""
    )


def draft_jira_tasks(text: str, human_input: str = ""):
    guidance_block = _build_guidance_block(human_input)

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

    # Tasks
    clean_and_translate_task = Task(
        description=(
            "Clean the spelling, grammar, and technical terminology of the following "
            f"raw English meeting transcript:\n\n{text}{guidance_block}"
        ),
        expected_output="A polished, structured meeting transcript in English, free from grammar errors and Whisper misinterpretations.",
        agent=transcript_editor
    )

    extract_action_items_task = Task(
        description=f"""Follow these steps strictly:
        1. Use the RAG tool EXACTLY ONCE with the query 'JIRA standards'.
        2. Read and memorize the returning formatting rules and priority logic.
        3. Analyze the English meeting record.
        4. Extract the action items and format them perfectly matching the company rules.
        5. Return the final bulleted list. DO NOT use the RAG tool a second time.
        6. Respect any additional human guidance if provided.{guidance_block}""",
        expected_output="A bulleted list of technical decisions and action items formatted exactly according to company standards.",
        agent=meeting_analyst,
        context=[clean_and_translate_task]
    )

    crew = Crew(
        agents=[transcript_editor, meeting_analyst],
        tasks=[clean_and_translate_task, extract_action_items_task],
        verbose=True
    )
    return crew.kickoff()


def create_jira_tasks(action_items: str, human_input: str = ""):
    guidance_block = _build_guidance_block(human_input)

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

    create_jira_tasks_task = Task(
        description=(
            "Create JIRA tasks from the approved action items below.\n\n"
            f"Approved action items:\n{action_items}\n\n"
            "Report the result of the tasks created using the JiraTaskCreator tool. "
            "Format strictly as:\n"
            "✅ - Task Summary: Successfully created."
            f"{guidance_block}"
        ),
        expected_output="A clean list of created JIRA tasks.",
        agent=jira_specialist
    )

    crew = Crew(
        agents=[jira_specialist],
        tasks=[create_jira_tasks_task],
        verbose=True
    )
    return crew.kickoff()


def _parse_action_items(action_items: str):
    lines = [line.strip() for line in action_items.splitlines() if line.strip()]
    cleaned = []
    for line in lines:
        normalized = line.lstrip("-*• ").strip()
        if normalized:
            cleaned.append(normalized)
    return cleaned


def _render_action_items(action_items_list):
    if not action_items_list:
        print("\nNo action items available.\n")
        return
    print("\n--- Action Items Pending Approval ---")
    for idx, item in enumerate(action_items_list, start=1):
        print(f"{idx}. {item}")
    print("-------------------------------------\n")


def _human_approval_screen(action_items: str) -> str:
    """
    Human-in-the-loop approval step before JIRA creation.
    Users can edit/delete/add items until they approve.
    """
    items = _parse_action_items(action_items)

    while True:
        _render_action_items(items)
        print("Commands:")
        print("  approve                     -> continue and create JIRA tasks")
        print("  edit <index>                -> edit one action item")
        print("  delete <index>              -> delete one action item")
        print("  add                         -> add a new action item")
        print("  cancel                      -> stop the flow")
        raw_cmd = input("Your command: ").strip()

        if not raw_cmd:
            continue

        lower_cmd = raw_cmd.lower()

        if lower_cmd == "approve":
            if not items:
                print("Cannot approve an empty list. Add at least one action item.")
                continue
            return "\n".join(f"- {item}" for item in items)

        if lower_cmd == "add":
            new_item = input("New action item: ").strip()
            if new_item:
                items.append(new_item)
            else:
                print("Empty action item ignored.")
            continue

        if lower_cmd == "cancel":
            raise RuntimeError("Human approval cancelled. JIRA tasks were not created.")

        tokens = raw_cmd.split(maxsplit=1)
        if len(tokens) != 2:
            print("Invalid command format.")
            continue

        action, raw_index = tokens[0].lower(), tokens[1].strip()
        if not raw_index.isdigit():
            print("Index must be a number.")
            continue

        index = int(raw_index) - 1
        if index < 0 or index >= len(items):
            print("Index out of range.")
            continue

        if action == "delete":
            removed = items.pop(index)
            print(f"Deleted: {removed}")
            continue

        if action == "edit":
            updated = input("Updated text: ").strip()
            if updated:
                items[index] = updated
            else:
                print("Empty update ignored.")
            continue

        print("Unknown command.")


def analyze_meeting(text: str, human_input: str = "", require_human_approval: bool = True):
    draft_result = draft_jira_tasks(text, human_input=human_input)
    approved_action_items = getattr(draft_result, "raw", str(draft_result))
    if require_human_approval:
        approved_action_items = _human_approval_screen(approved_action_items)
    return create_jira_tasks(approved_action_items, human_input=human_input)