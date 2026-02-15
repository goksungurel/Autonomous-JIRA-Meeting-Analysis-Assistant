**Meeting Analysis & JIRA Task Assistant (Local RAG)**

This project is a privacy-focused, Local AI Assistant designed to analyze meeting transcripts and autonomously generate structured JIRA tasks. It is built with a focus on data privacy, executing entirely on local infrastructure without external API dependencies.

🚀 Core Capabilities
Autonomous Analysis: Uses CrewAI to orchestrate multiple agents that summarize transcripts and identify action items.

Local RAG Architecture: Employs a Retrieval-Augmented Generation pipeline to cross-reference organizational standards stored in a local knowledge base.

Privacy-First Execution: Powered by Ollama, using Llama 3 for reasoning and Nomic-Embed-Text for vector embeddings, ensuring all data remains on the local machine.

Professional JIRA Output: Generates tasks with specific titles, descriptions, priority levels, and acceptance criteria based on the meeting context.

Streamlit UI: A clean and functional web interface for seamless document uploading and real-time processing.

🛠️ Tech Stack
Orchestration: CrewAI

Local LLM: Llama 3 (via Ollama)

Vector Database: Local RAG via Nomic-Embed-Text

Frontend: Streamlit

Development: Cursor (AI-Native IDE)

📸 Project Overview
<img width="1581" height="1098" alt="Screenshot 2026-02-15 at 16 58 37" src="https://github.com/user-attachments/assets/8b847a2c-7970-4e61-a87d-237e12212e55" />

<img width="1581" height="1098" alt="Screenshot 2026-02-15 at 16 59 22" src="https://github.com/user-attachments/assets/dc9e7c25-3d90-4a6d-b113-1765130fab79" />

<img width="1581" height="1098" alt="Screenshot 2026-02-15 at 17 08 01" src="https://github.com/user-attachments/assets/6555b2cf-d263-4651-b7a9-093ec806ab1b" />


**RAG-Powered Task Generation**

The system retrieves organizational guidelines from the /bilgi_tabanı directory to ensure all generated tasks meet quality standards.

**Functional Dashboard**

Minimalist UI focused on productivity and system transparency.

🎓 About the Project
Developed by a 3rd-year Software Engineering student as a portfolio piece to demonstrate expertise in Agentic AI, RAG systems, and Local LLM deployment. The project highlights the ability to bridge the gap between complex AI logic and user-friendly software products.
