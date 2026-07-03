# Autonomous JIRA & Meeting Analysis Assistant (Multi-Agent RAG)

A privacy-first, local AI assistant that:

- transcribes meeting audio with Whisper,
- optionally adds speaker diarization with pyannote,
- cleans and converts the transcript into professional English (local LLM via Ollama),
- extracts actionable decisions using local RAG rules from `knowledge_base/`,
- and creates one JIRA task per action item (currently mocked by default in code).

This repository includes a Streamlit UI so you can run the full workflow from your browser.

## Core value proposition

- **Privacy-first execution:** LLM and embeddings run locally with Ollama (`llama3`, `nomic-embed-text`).
- **Tiered agentic workflow:** A 3-agent CrewAI pipeline transforms raw meeting content into structured task output.
- **Local RAG standards:** Action items are aligned with internal rules stored in `knowledge_base/`.
- **Human-in-the-loop approval:** JIRA creation now requires explicit user approval in the UI before any task write step.

## What this project does

### End-to-end flow

```text
Audio (.mp3/.wav) or Transcript (.txt)
        ↓
Whisper transcription
        ↓
(Optional) Speaker diarization (pyannote)
        ↓
Agent 1: Transcript Editor (clean + normalize + English meeting record)
        ↓
Agent 2: Meeting Analyst (RAG: read "JIRA standards" once)
        ↓
Draft task suggestions shown to user
        ↓
Human approval step in UI
        ↓
Agent 3: JIRA Specialist (creates approved tasks)
```

### Multi-agent architecture (CrewAI)

- **Senior Transcript Editor:** fixes grammar, Whisper errors/hallucinations, and produces a structured English meeting record.
- **IT Meeting Analyst:** queries local knowledge once (RAG) for "JIRA standards", then extracts action items in required format.
- **JIRA Operations Specialist:** creates one task per approved action item through the tool interface.

## Tech stack

- **UI:** Streamlit (`app.py`)
- **Agent orchestration:** CrewAI (`meeting_assistant.py`)
- **Local LLM + embeddings:** Ollama (`llama3`, `nomic-embed-text`)
- **Speech-to-text:** OpenAI Whisper (`transcription.py`)
- **Speaker diarization (optional):** `pyannote.audio` (requires Hugging Face token)
- **RAG rules / standards:** Markdown files in `knowledge_base/`
- **Session history:** SQLite (`database.py`) — meetings and JIRA outputs persisted locally

## Repository structure

- `app.py`: Streamlit UI for upload, transcription, draft task generation, and approval-based JIRA creation.
- `meeting_assistant.py`: 3-agent CrewAI logic, RAG integration, and JIRA tool.
- `transcription.py`: Whisper transcription functions (+ optional diarization).
- `database.py`: SQLite helpers for persisting meeting history.
- `knowledge_base/meeting_rules_and_samples.md`: sample standards and "JIRA rules" used by RAG.
- `requirements.txt`: Python dependencies.
- `tests/`: Unit tests for pure utility functions and database operations (run with `pytest`).

## Prerequisites

### System requirements

- macOS / Linux recommended
- Python 3.10+
- `ffmpeg` installed (needed by Whisper for many audio formats)

### Ollama setup (local LLM + embeddings)

1. Install Ollama using the official instructions.
2. Start Ollama server (default: `http://localhost:11434`).
3. Pull required models:

```bash
ollama pull llama3:latest
ollama pull nomic-embed-text
```

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

For optional diarization support, uncomment `pyannote.audio` in `requirements.txt` before installing.

## Environment variables

Create a `.env` file in the project root:

```bash
# Optional (for diarization)
HF_TOKEN="your_huggingface_token"

# Optional (for real JIRA API calls)
JIRA_URL="https://your-domain.atlassian.net"
JIRA_EMAIL="you@company.com"
JIRA_TOKEN="your_jira_api_token"
JIRA_PROJECT_KEY="KAN"
```

## Run the app

```bash
streamlit run app.py
```

Then:

1. Upload `.txt` transcript or `.mp3`/`.wav` audio.
2. If audio, select the **audio language** (English by default) and optionally enable diarization, then click **Transcribe Audio (Whisper)**.
3. Add optional **Human Input** guidance.
4. Click **Generate Task Suggestions**.
5. Review and edit draft tasks.
6. Click **Approve & Create Tasks on JIRA** to proceed, or reject the draft.
7. Approved meetings are saved automatically — view past meetings in the **Meeting History** sidebar.

## Speaker diarization (optional)

If enabled, `transcription.py` uses `pyannote/speaker-diarization-3.1` and requires:

- `HF_TOKEN` with model access,
- installation of `pyannote.audio` (not in `requirements.txt` by default).

## JIRA integration status

`JiraTaskTool` currently runs in mock mode — it returns a simulated key (e.g., `KAN-123`) without making any real API calls. This lets the app run without credentials.

To enable real JIRA task creation:

1. Uncomment the real API block in `JiraTaskTool._run` inside `meeting_assistant.py`.
2. Set the following in your `.env`:

```bash
JIRA_URL="https://your-domain.atlassian.net"
JIRA_EMAIL="you@company.com"
JIRA_TOKEN="your_jira_api_token"
JIRA_PROJECT_KEY="KAN"
```

## Running tests

```bash
pytest tests/
```

Tests cover pure utility functions (`_parse_action_items`, `_action_items_to_markdown`, `JiraTaskTool` mock behavior) and all database operations. All tests run without Ollama or JIRA credentials.

## Customizing RAG rules

The analyst agent is instructed to query RAG exactly once with `"JIRA standards"`.
Update standards in:

- `knowledge_base/meeting_rules_and_samples.md`

Typical customizations:

- team prefixes (`[Backend]`, `[Frontend]`, `[Mobile]`, etc.),
- priority rules,
- tag conventions,
- output examples/templates.

## Troubleshooting

### "Whisper is not installed"

```bash
pip install openai-whisper
```

### Ollama connection errors

- Ensure Ollama is running.
- Ensure base URL is `http://localhost:11434`.
- Ensure `llama3:latest` and `nomic-embed-text` are pulled.

### Diarization errors

- Ensure `HF_TOKEN` is set.
- Ensure `pyannote.audio` is installed and model access is granted on Hugging Face.

## Privacy and data handling

- LLM reasoning and embeddings run locally via Ollama.
- Audio/transcripts are processed on your machine.
- If real JIRA integration is enabled, approved tasks are sent to your JIRA instance.

