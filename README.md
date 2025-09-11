# Medical Knowledge Assistant  
From AGENTIC RAG to Reality: Building a Medical Knowledge Assistant with Streaming, Clinical Trials & Agentic Workflows

This project implements a production-ready medical knowledge assistant, combining retrieval-augmented generation (RAG), multi-step/agentic reasoning workflows, clinical trials integration, and streaming responses. It supports exploratory medical queries and returns evidence, summaries, reasoning steps, and relevant trials — via a clean UI.

---

## Features

- **Agentic RAG pipeline**: multi-node workflow: classify → retrieve/refine → rank → fetch trials → summarize → explain  
- **Streaming responses**: uses SSE (Server‐Sent Events) so users see progress in real time  
- **ClinicalTrials.gov integration**: fetches full studies related to the query  
- **Interactive UI**: built with Streamlit to show the workflow steps and final output side by side  
- **Off-domain detection**: if a query is non-medical, the system stops further processing  
- **Query refinement**: if initial retrieval fails, automatically refines the query (up to 2 times) before concluding no answer  

---

## Tech Stack

| Component | Used Tools / Libraries |
|-----------|--------------------------|
| Backend API | FastAPI, SSE, HTTPx |
| Workflow engine | LangGraph (state graph of nodes) |
| Retrieval | PubMed retriever |
| LLM / Generation | Google Gemini (“gemini-2.0-flash”) (via LangChain, etc.) |
| Frontend / UI | Streamlit |
| Environment management | Python 3.10+, dotenv, SSL improvements, etc. |

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/medical-knowledge-assistant.git
   cd medical-knowledge-assistant


Structure & Key Components

Here’s an outline of the project structure and what each part does:

├── app/
│   ├── config.py           # configuration: LLM setup, retriever, SSL patching
│   ├── state.py            # definition of AgentState datatype
│   ├── prompts/            # prompt templates: classify, refine, summarize, explanation
│   ├── nodes/              # individual workflow nodes: classify, retrieve, refine, fetch_trials, summarize, explain, etc.
│   ├── workflow.py         # builds the LangGraph state graph and compiles the workflow
│   └── api.py              # FastAPI app with /ask endpoint for streaming
├── ui/
│   └── streamlit_app.py    # Streamlit front end for user interaction
├── requirements.txt        # required Python libraries
├── .env.example            # template for environment variables
└── README.md               # this file


