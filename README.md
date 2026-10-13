# 🧠 Multi-Agent RAG Research System

[![LangGraph](https://img.shields.io/badge/Orchestrator-LangGraph-blue?logo=python&logoColor=white)](https://github.com/langchain-ai/langgraph)
[![Gemini](https://img.shields.io/badge/LLM-Gemini_3.5_Flash_Lite-8E75B2?logo=google&logoColor=white)](https://ai.google.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/Frontend-React_19_%2B_TypeScript-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind_CSS_v4-38B2AC?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Vite](https://img.shields.io/badge/Bundler-Vite-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)

An autonomous, stateful **Multi-Agent Research & Retrieval-Augmented Generation (RAG)** platform powered by **LangGraph**, **Google Gemini**, and a real-time reactive **React + TypeScript** console. 

The system coordinates specialized autonomous agents to dynamically plan queries, retrieve knowledge from internal indexed documents, conduct live external web research, evaluate retrieval sufficiency through closed-loop feedback, and support **Human-in-the-Loop (HITL)** checkpointing with state persistence.

---

## 📌 Architecture Overview

### Core Workflow Lifecycle
1. **User Query Input**: The user submits a research question via the Web UI or CLI.
2. **Supervisor Agent (Orchestrator)**: Evaluates query intent, extracts distilled 3–7 word search keywords, and determines the routing path (`rag`, `research`, or `both`).
3. **Internal RAG Agent**: Performs token-frequency and BM25-style lexical matching against the internal indexed knowledge base (PDFs, Markdown docs, architecture benchmarks).
4. **External Web Research Agent**: Queries live web search engines (DuckDuckGo Search) to gather real-time facts, documentation, and external references.
5. **Evaluator Agent (Quality Gate & Feedback Loop)**:
   - Evaluates gathered context against the user's inquiry, computing a 0–100 quality score and sufficiency verdict.
   - **Self-Correction Loop**: If information is insufficient and within iteration limits (`iteration_count < max_iterations`), routes back to the Supervisor Agent with structured critique and missing topics.
   - **HITL Escalation**: If maximum iterations are reached or human intervention is requested, triggers an execution pause at a persistent checkpoint.
6. **Human-in-the-Loop (HITL) Checkpoint**: Employs LangGraph's `interrupt_before=["human_node"]` with `MemorySaver` thread persistence, allowing human operators to inspect intermediate findings, provide steering feedback, and approve resumption.
7. **Response Agent (Synthesizer)**: Consolidates internal KB context, web citations, evaluation feedback, and human instructions into an authoritative, structured research report with references.

---

## 🚀 Key Features

- **Multi-Agent Collaboration via LangGraph**: Explicit StateGraph orchestrating specialized agent nodes through shared TypedDict state, conditional edges, and handoffs.
- **Closed-Loop Evaluator-Optimizer**: Automated self-correction where the Evaluator critiques context sufficiency and triggers targeted secondary research before answer generation.
- **Stateful Human-in-the-Loop (HITL)**: Built-in thread checkpointing with `MemorySaver` enabling human review, query redirection, and state resumption without data loss.
- **Hybrid Retrieval Strategy**: Combines internal knowledge base lookup with real-time web search (DuckDuckGo API) with automatic rate-limit fallback synthesis.
- **Real-Time SSE Streaming**: FastAPI server streams node updates, intermediate reasoning steps, source citations, and evaluation metrics to the UI via Server-Sent Events (`EventSourceResponse`).
- **Interactive Visual Canvas**: React frontend includes an interactive SVG LangGraph execution canvas displaying active agent nodes and data pipelines in real time.
- **Dual-Mode Operation**: Run queries interactively via the modern Web Console or autonomously via the terminal CLI runner.

---

## 🤖 Agent Roles & Specialization

| Agent | Module | Description |
|---|---|---|
| **Supervisor Agent** | `agents/supervisor.py` | Central coordinator; plans query execution, synthesizes distilled search queries, and selects next routing path (`rag` / `research` / `both` / `response`). |
| **RAG Agent** | `agents/rag_agent.py` | Retrieves structured domain knowledge from the internal index using term matching and tag-weighted BM25 scoring. |
| **Research Agent** | `agents/research_agent.py` | Searches external web sources via DuckDuckGo, pulling snippets, articles, and external technical benchmarks. |
| **Evaluator Agent** | `agents/evaluator.py` | Quality assurance node; verifies context completeness, assigns 0–100 score, formulates missing information criteria, and controls loop retries. |
| **Human Node (HITL)** | `agents/human_node.py` | Checkpoint interrupt node; pauses pipeline for human inspection, custom prompt steering, or one-click approval. |
| **Response Agent** | `agents/response_agent.py` | Final synthesis engine; writes Markdown reports with Executive Summaries, Key Technical Insights, and source citations. |

---

## 📁 Repository Structure

```text
Multi_Agent_RAG_Research_System/
├── MultiAgentRAGSystem.jpg       # High-level architecture flow diagram
├── backend/
│   ├── .env                      # API keys (GEMINI_API_KEY)
│   ├── main.py                   # CLI execution runner & HITL terminal demo
│   ├── server.py                 # FastAPI SSE streaming backend server
│   ├── requirements.txt          # Python dependencies
│   ├── agents/
│   │   ├── llm.py                # ChatGoogleGenerativeAI (Gemini 3.5 Flash Lite) setup
│   │   ├── supervisor.py         # Supervisor routing agent
│   │   ├── rag_agent.py          # Internal KB retriever agent & seeded documents
│   │   ├── research_agent.py     # External DuckDuckGo web search agent
│   │   ├── evaluator.py          # Evaluator quality gate agent
│   │   ├── human_node.py         # HITL interrupt checkpoint node
│   │   └── response_agent.py     # Multi-source synthesis response agent
│   └── graph/
│       ├── state.py              # LangGraph ResearchState TypedDict schema
│       └── workflow.py           # StateGraph assembly, conditional edges & checkpointer
└── frontend/
    ├── index.html                # Single-page application entry point
    ├── package.json              # Node dependencies & build scripts
    ├── vite.config.ts            # Vite config with backend API proxy (/api -> :8000)
    └── src/
        ├── api/
        │   └── client.ts         # SSE streaming client & REST API calls
        ├── components/
        │   ├── AgentBadge.tsx     # Color-coded agent role badges
        │   ├── AgentNodeGraph.tsx # Live SVG LangGraph state machine visualization
        │   ├── HITLModal.tsx      # Checkpoint review & feedback steering modal
        │   ├── ReasoningCard.tsx  # Collapsible step-by-step reasoning accordion
        │   └── ResearchConsole.tsx# Full interactive research dashboard
        ├── App.tsx               # Root component
        └── main.tsx              # React mounting root
```

---

## ⚙️ Installation & Setup

### Prerequisites
- **Python**: 3.10, 3.11, or 3.12
- **Node.js**: v18+ (v20+ recommended) and `npm`
- **Google Gemini API Key**: Obtain a key from [Google AI Studio](https://aistudio.google.com/)

---

### 1. Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create or verify a `.env` file in the `backend/` directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Start the FastAPI Backend Server**:
   ```bash
   uvicorn server:api_app --reload --host 127.0.0.1 --port 8000
   ```
   *The backend will be accessible at `http://127.0.0.1:8000` with Swagger docs at `http://127.0.0.1:8000/docs`.*

---

### 2. Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install frontend dependencies**:
   ```bash
   npm install
   ```

3. **Start Vite Development Server**:
   ```bash
   npm run dev
   ```
   *The frontend dashboard will be available at `http://localhost:5173`.*

---

## 💻 Usage

### Option A: Interactive Web Console
1. Open `http://localhost:5173` in your browser.
2. Select an example query or enter a custom technical question.
3. Observe real-time agent handoffs on the **LangGraph Execution Canvas**.
4. Expand reasoning cards to inspect intermediate agent thoughts and source citations.
5. When prompted by a **Human Checkpoint**, provide steering feedback or click **Approve Resumption** to continue.

### Option B: Terminal CLI Runner
You can run the full multi-agent pipeline directly from the command line without the frontend:

```bash
cd backend
python main.py "Compare LangGraph multi-agent coordination with traditional RAG pipelines."
```

#### Running the Human-in-the-Loop (HITL) CLI Demo
Demonstrates LangGraph state checkpointing, workflow interruption, manual feedback injection, and state resumption:

```bash
cd backend
python main.py --hitl
```

---

## 📡 API Reference

### Health Check
- **Endpoint**: `GET /api/health`
- **Response**:
  ```json
  { "status": "ok", "app": "MultiAgentRAGSystem", "version": "1.0.0" }
  ```

### Knowledge Base Documents
- **Endpoint**: `GET /api/documents`
- **Description**: Returns the list of pre-indexed internal technical documents.

### Research Stream (Server-Sent Events)
- **Endpoint**: `POST /api/research/stream`
- **Request Body**:
  ```json
  {
    "query": "Evaluate BM25 retrieval vs dense vector embeddings in multi-agent workflows.",
    "thread_id": "optional-uuid-string",
    "max_iterations": 2,
    "force_hitl": false
  }
  ```
- **SSE Events Emitted**:
  - `pipeline_start`: Graph initialization and thread creation.
  - `agent_step`: Real-time node outputs, thoughts, execution times, and sources.
  - `hitl_checkpoint`: Triggered when the graph pauses at `human_node`.
  - `final_answer`: Final synthesized report with metrics.
  - `error`: Pipeline error diagnostics.

### Resume HITL Checkpoint
- **Endpoint**: `POST /api/research/approve`
- **Request Body**:
  ```json
  {
    "thread_id": "thread-123456",
    "human_feedback": "Emphasize memory checkpointing and SqliteSaver capabilities.",
    "max_iterations": 3
  }
  ```
- **Response**: Resumes execution from the exact saved checkpoint and returns the synthesized response.

---

## 📊 State Schema (`ResearchState`)

The shared LangGraph state passed between agents is defined as a `TypedDict` in `backend/graph/state.py`:

```python
class ResearchState(TypedDict, total=False):
    query: str                      # User's initial research prompt
    search_query: Optional[str]     # Distilled query synthesized by Supervisor
    messages: List[Dict[str, Any]]  # Execution audit log and agent handoffs
    next_agent: str                 # Dynamic routing destination
    rag_results: List[Dict[str, Any]] # Documents retrieved from internal KB
    research_results: List[Dict[str, Any]] # Snippets retrieved from web search
    evaluation: Dict[str, Any]      # Sufficiency score, feedback & missing topics
    iteration_count: int            # Current evaluator feedback iteration
    max_iterations: int             # Threshold before HITL escalation
    human_feedback: Optional[str]   # Feedback injected by human operator
    human_approved: bool            # Approval flag to bypass loop
    final_answer: str               # Synthesized markdown report
    errors: List[str]               # Error records
```

---

## 🛠️ Technology Stack

- **Orchestration**: [LangGraph](https://github.com/langchain-ai/langgraph) (StateGraph, MemorySaver)
- **Language Models**: [LangChain Google GenAI](https://python.langchain.com/docs/integrations/chat/google_generative_ai/) (`gemini-3.5-flash-lite`)
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/), [SSE-Starlette](https://github.com/sysid/sse-starlette)
- **Web Search**: [DuckDuckGo Search](https://github.com/deedy5/duckduckgo_search) (`duckduckgo-search`)
- **Frontend**: [React 19](https://react.dev/), [TypeScript](https://www.typescriptlang.org/), [Vite](https://vitejs.dev/)
- **Styling & UI**: [Tailwind CSS v4](https://tailwindcss.com/), [Lucide React](https://lucide.dev/)


