# 🤖 Autonomous JIRA & Meeting Analysis Assistant (Multi-Agent RAG)

A **privacy-first**, local AI solution designed to transcribe Turkish meetings, translate them into technical English, and autonomously generate structured JIRA tasks using a **Multi-Agent Orchestration** and **Local RAG** architecture.

## 🚀 Core Value Proposition

* **Privacy-First Execution:** Powered by **Ollama (Llama 3)** and **Nomic-Embed-Text**, ensuring 100% of meeting data stays on the local machine. No external LLM APIs are used for reasoning.
* **Tiered Agentic Workflow:** Uses a sophisticated 3-agent pipeline (Editor, Analyst, Specialist) to manage context transitions from raw audio to professional project management outputs.
* **Automated Translation & Correction:** Features a specialized agent that bridges the gap between Turkish audio and English technical standards, fixing Whisper-specific hallucinations (e.g., "ilkkağ" → "HR") in real-time.
* **Local RAG (Retrieval-Augmented Generation):** Cross-references extracted decisions with organizational standards (stored in `/knowledge_base`) to automate priority levels and team tagging.

## 🛠️ The Agentic Pipeline

Our system employs three specialized agents via **CrewAI** to ensure high-fidelity task generation:

1.  **Senior Transcript Editor & Translator:** Captures raw Turkish output, corrects grammar, resolves technical jargon, and translates the entire context into formal technical English.
2.  **IT Meeting Analyst:** Analyzes the structured English transcript to identify key deliverables, sprint goals, and technical requirements.
3.  **JIRA Operations Specialist:** Autonomously interacts with the **Atlassian JIRA API** to create individual tasks with specific summaries, descriptions, and metadata derived from the RAG rules.

## 💻 Tech Stack

- **Orchestration:** CrewAI
- **Local LLM & Embeddings:** Llama 3 & Nomic-Embed-Text (via Ollama)
- **Speech-to-Text:** OpenAI Whisper (enhanced with technical `initial_prompt`)
- **Speaker Diarization:** pyannote.audio 3.1
- **Interface:** Streamlit
- **Infrastructure:** Python 3.13 / Atlassian-Python-API

## 🔄 How It Works
```text
Raw Audio (.mp3/.wav)
      ↓
  Whisper + Pyannote (Diarized Turkish Transcript)
      ↓
  Agent 1: Clean, Fix Hallucinations & Translate to English
      ↓
  Agent 2: Extract Action Items + Query Local Knowledge Base (RAG)
      ↓
  Agent 3: Execute JIRA API calls for each identified task
      ↓
  JIRA Board Updated ✅
```

## 📚 RAG-Powered Task Generation

The system retrieves organizational guidelines from the `/knowledge_base` directory to ensure all generated tasks meet quality standards, including:
- **Priority Logic:** Automatically assigns High/Medium/Low based on deadline, urgency, and customer impact.
- **Team Assignment:** Routes tasks to [Backend], [Frontend], [Mobile], or [Data] teams based on context.
- **Naming Conventions:** Enforces standardized JIRA summary formats and label suggestions (e.g., hotfix, performance, technical-debt).

## 🎓 About the Project

Developed by **Göksun**, a 3rd-year Software Engineering student at **Izmir University of Economics**, as a portfolio piece to demonstrate expertise in **Agentic AI**, **RAG Systems**, **NLP Pipelines**, and **Local LLM Deployment**. 

The project highlights the ability to bridge the gap between complex autonomous AI logic and enterprise-grade software products (JIRA integration), with a strong focus on data privacy and local-first infrastructure.
