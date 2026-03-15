# Meeting Analysis & JIRA Task Assistant (Local RAG)

This project is a privacy-focused, Local AI Assistant designed to analyze meeting transcripts and autonomously generate structured JIRA tasks. It is built with a focus on data privacy, executing entirely on local infrastructure without external API dependencies.

## 🚀 Core Capabilities

**Autonomous Analysis:** Uses CrewAI to orchestrate multiple agents that summarize transcripts and identify action items.

**Local RAG Architecture:** Employs a Retrieval-Augmented Generation pipeline to cross-reference organizational standards stored in a local knowledge base.

**Privacy-First Execution:** Powered by Ollama, using Llama 3 for reasoning and Nomic-Embed-Text for vector embeddings, ensuring all data remains on the local machine.

**Professional JIRA Output:** Generates tasks with specific titles, descriptions, priority levels, and acceptance criteria based on the meeting context.

**Speaker Diarization:** Automatically identifies who said what in meeting recordings using pyannote.audio 3.1 + Whisper. Output format: `[SPEAKER_00 - 00:03]: Payment integration is complete.`

**Streamlit UI:** A clean and functional web interface for seamless document uploading and real-time processing.

## 🛠️ Tech Stack

- **Orchestration:** CrewAI
- **Local LLM:** Llama 3 (via Ollama)
- **Vector Database:** Local RAG via Nomic-Embed-Text
- **Speech-to-Text:** OpenAI Whisper
- **Speaker Diarization:** pyannote.audio 3.1
- **JIRA Integration:** Atlassian JIRA API (automatic task creation)
- **Frontend:** Streamlit
- **Development:** Cursor (AI-Native IDE)

## 🔄 How It Works
```
Audio/Text File
      ↓
  Whisper (speech-to-text)
      ↓
  pyannote.audio (who said what?)
      ↓
  Agent 1: Extract decisions + RAG knowledge base
      ↓
  Agent 2: Convert to JIRA format
      ↓
  JIRA API → Tasks created automatically ✅
```

## 📚 RAG-Powered Task Generation

The system retrieves organizational guidelines from the `/bilgi_tabani` directory to ensure all generated tasks meet quality standards, including priority rules, team assignments, and labeling conventions.

## 🎓 About the Project

Developed by a 3rd-year Software Engineering student as a portfolio piece to demonstrate expertise in Agentic AI, RAG systems, NLP pipelines, and Local LLM deployment. The project highlights the ability to bridge the gap between complex AI logic and user-friendly software products.