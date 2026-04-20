# Autonomous JIRA & Meeting Analysis Assistant (Multi‑Agent RAG)

A privacy-first, local AI assistant that:

- transcribes Turkish meeting audio (Whisper),
- optionally adds speaker diarization (pyannote),
- cleans and converts the transcript into professional English (local LLM via Ollama),
- extracts actionable decisions using **local RAG** rules from `knowledge_base/`,
- and creates one JIRA task per action item (currently **mocked** by default in code).

This repository includes a Streamlit UI so you can run the full workflow from your browser.

## What this project does

### End-to-end flow

```text
Audio (.mp3/.wav) or Transcript (.txt)
        ↓
Whisper transcription (Turkish audio → text)
        ↓
(Optional) Speaker diarization (pyannote) → "who said what"
        ↓
Agent 1: Transcript Editor (clean + normalize + English meeting record)
        ↓
Agent 2: Meeting Analyst (RAG: read "JIRA standards" once from knowledge base)
        ↓
Agent 3: JIRA Specialist (create tasks for each action item)
```

### Multi-agent architecture (CrewAI)

- **Senior Transcript Editor**: fixes grammar, Whisper errors/hallucinations, and produces a structured English meeting record.
- **IT Meeting Analyst**: queries the local knowledge base once (RAG) for “JIRA standards”, then extracts action items in the required format.
- **JIRA Operations Specialist**: creates one task per action item via a tool interface.

## Tech stack

- **UI**: Streamlit (`app.py`)
- **Agent orchestration**: CrewAI (`meeting_assistant.py`)
- **Local LLM + embeddings**: Ollama (`llama3`, `nomic-embed-text`)
- **Speech-to-text**: OpenAI Whisper (`transcription.py`)
- **Speaker diarization (optional)**: `pyannote.audio` (requires Hugging Face token)
- **RAG rules / standards**: Markdown files in `knowledge_base/`

## Repository structure

- `app.py`: Streamlit UI. Upload `.txt` or `.mp3/.wav`, transcribe if needed, then run the agents.
- `meeting_assistant.py`: the 3-agent CrewAI pipeline + RAG tool + JIRA tool implementation.
- `transcription.py`: Whisper transcription functions (+ optional diarization).
- `knowledge_base/meeting_rules_and_samples.md`: sample standards and “JIRA rules” used by RAG.
- `requirements.txt`: minimal Python dependencies used by the demo.

## Prerequisites

### System requirements

- macOS / Linux recommended
- Python environment (this repo targets modern Python; Streamlit + Whisper often work best on Python 3.10+)
- `ffmpeg` installed (Whisper typically relies on it for many audio formats)

### Ollama setup (local LLM + embeddings)

1. Install Ollama: see the official Ollama instructions.
2. Start the Ollama server (it usually listens on `http://localhost:11434`).
3. Pull the models used by this project:

```bash
ollama pull llama3:latest
ollama pull nomic-embed-text
```

## Installation

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Notes:

- `requirements.txt` is intentionally minimal for a simple demo. If you enable diarization or real JIRA integration, you may need to install extra packages (see sections below).

## Environment variables

Create a `.env` file in the project root (it’s already ignored by git). Example:

```bash
# Optional (only needed if you enable diarization)
HF_TOKEN="your_huggingface_token"

# Optional (only needed if you enable real JIRA API calls)
JIRA_URL="https://your-domain.atlassian.net"
JIRA_EMAIL="you@company.com"
JIRA_TOKEN="your_jira_api_token"
JIRA_PROJECT_KEY="KAN"
```

## Run the app

Start the Streamlit UI:

```bash
streamlit run app.py
```

Then:

- upload a `.txt` meeting transcript, or
- upload an audio file (`.mp3` / `.wav`) and click **Transcribe Audio (Whisper)**,
- optionally enable diarization,
- click **Run Autonomous Agents & Sync with JIRA**.

## Speaker diarization (optional)

If you enable diarization in the UI, `transcription.py` uses `pyannote/speaker-diarization-3.1` and requires:

- a Hugging Face access token (`HF_TOKEN`) with access to the model,
- installing `pyannote.audio` (not included in `requirements.txt` by default).

## JIRA integration status (important)

### Current default behavior (safe demo mode)

In `meeting_assistant.py`, the JIRA tool currently **does not call Atlassian**. Instead, it prints a mock message and returns a fake key like `KAN-123`. This makes the project runnable without credentials and avoids accidental writes.

### Enabling real JIRA task creation

`meeting_assistant.py` already contains the real Atlassian API logic inside `JiraTaskTool._run`, but it is wrapped in a triple-quoted block and replaced by a mock implementation.

To enable real creation you would:

- restore the real API call code in `JiraTaskTool._run`,
- ensure `.env` contains valid `JIRA_URL`, `JIRA_EMAIL`, `JIRA_TOKEN`, `JIRA_PROJECT_KEY`,
- install the Atlassian client library (e.g., `atlassian-python-api`) and `python-dotenv` if missing from your environment.

## Customizing RAG rules

The meeting analyst agent is instructed to query the RAG tool **exactly once** with the query `"JIRA standards"`. You can update the standards in:

- `knowledge_base/meeting_rules_and_samples.md`

Typical customizations:

- team prefixes (`[Backend]`, `[Frontend]`, `[Mobile]`, …),
- priority rules,
- tag conventions,
- examples and templates used by the analyst agent.

## Troubleshooting

### “Whisper is not installed”

Install it and re-run:

```bash
pip install openai-whisper
```

### Ollama connection errors

Make sure:

- Ollama is running,
- the base URL matches `http://localhost:11434`,
- you pulled the required models (`llama3:latest`, `nomic-embed-text`).

### Diarization errors

- Ensure `HF_TOKEN` is set.
- Ensure you installed `pyannote.audio` and have access to the diarization model on Hugging Face.

## Privacy and data handling

- The LLM reasoning and embeddings are designed to run locally via Ollama.
- Audio/transcripts are processed locally on your machine.
- If you enable real JIRA integration, the extracted tasks will be sent to your JIRA instance.

