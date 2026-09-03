"""Tests for the CrewAI wiring in meeting_assistant.py.

Crew.kickoff() and rag_tool.add() would otherwise call a local Ollama server,
so both are stubbed here — these tests only verify that draft_jira_tasks and
create_jira_tasks build the right agents/tasks and return whatever the crew
produces, not that a real LLM produces good output.
"""
import pytest
import meeting_assistant


class _FakeCrew:
    """Stand-in for crewai.Crew that skips real LLM execution."""

    last_instance = None

    def __init__(self, agents, tasks, verbose=True):
        self.agents = agents
        self.tasks = tasks
        self.verbose = verbose
        type(self).last_instance = self

    def kickoff(self):
        return "FAKE_CREW_RESULT"


@pytest.fixture(autouse=True)
def fake_crew(monkeypatch):
    monkeypatch.setattr(meeting_assistant, "Crew", _FakeCrew)


@pytest.fixture(autouse=True)
def skip_rag_loading(monkeypatch):
    """draft_jira_tasks() calls _ensure_knowledge_base_loaded(); pretend it
    already ran so no embedding call is made. The loader itself is covered
    by its own tests below."""
    monkeypatch.setattr(meeting_assistant, "_knowledge_base_loaded", True)


def test_build_guidance_block_empty_for_blank_input():
    assert meeting_assistant._build_guidance_block("") == ""
    assert meeting_assistant._build_guidance_block("   ") == ""
    assert meeting_assistant._build_guidance_block(None) == ""


def test_build_guidance_block_includes_stripped_text():
    result = meeting_assistant._build_guidance_block("  focus on backend  ")
    assert "focus on backend" in result
    assert result.startswith("\n\nAdditional human guidance from the user:")


def test_draft_jira_tasks_returns_crew_result():
    result = meeting_assistant.draft_jira_tasks("Team discussed API v2 rollout.")
    assert result == "FAKE_CREW_RESULT"


def test_draft_jira_tasks_wires_two_agents_and_tasks():
    meeting_assistant.draft_jira_tasks("Team discussed API v2 rollout.")
    crew = _FakeCrew.last_instance
    assert len(crew.agents) == 2
    assert len(crew.tasks) == 2
    assert crew.agents[0].role == "Senior Transcript Editor"
    assert crew.agents[1].role == "IT Meeting Analyst"


def test_draft_jira_tasks_includes_transcript_in_first_task():
    meeting_assistant.draft_jira_tasks("Onboarding docs are missing.")
    crew = _FakeCrew.last_instance
    assert "Onboarding docs are missing." in crew.tasks[0].description


def test_draft_jira_tasks_appends_human_guidance():
    meeting_assistant.draft_jira_tasks("Some transcript.", human_input="Prioritize backend.")
    crew = _FakeCrew.last_instance
    assert "Prioritize backend." in crew.tasks[0].description
    assert "Prioritize backend." in crew.tasks[1].description


def test_create_jira_tasks_returns_crew_result():
    result = meeting_assistant.create_jira_tasks("- Fix login bug")
    assert result == "FAKE_CREW_RESULT"


def test_create_jira_tasks_wires_one_agent_and_task():
    meeting_assistant.create_jira_tasks("- Fix login bug")
    crew = _FakeCrew.last_instance
    assert len(crew.agents) == 1
    assert len(crew.tasks) == 1
    assert crew.agents[0].role == "JIRA Operations Specialist"
    assert "Fix login bug" in crew.tasks[0].description


def test_ensure_knowledge_base_loaded_calls_add_once(monkeypatch):
    monkeypatch.setattr(meeting_assistant, "_knowledge_base_loaded", False)
    calls = []
    monkeypatch.setattr(
        type(meeting_assistant.rag_tool), "add", lambda self, **kwargs: calls.append(kwargs)
    )

    meeting_assistant._ensure_knowledge_base_loaded()
    meeting_assistant._ensure_knowledge_base_loaded()

    assert len(calls) == 1
    assert meeting_assistant._knowledge_base_loaded is True


def test_ensure_knowledge_base_loaded_skips_missing_directory(monkeypatch, tmp_path):
    monkeypatch.setattr(meeting_assistant, "_knowledge_base_loaded", False)
    monkeypatch.setattr(meeting_assistant, "_knowledge_base", tmp_path / "does_not_exist")
    calls = []
    monkeypatch.setattr(
        type(meeting_assistant.rag_tool), "add", lambda self, **kwargs: calls.append(kwargs)
    )

    meeting_assistant._ensure_knowledge_base_loaded()

    assert calls == []
    assert meeting_assistant._knowledge_base_loaded is True
