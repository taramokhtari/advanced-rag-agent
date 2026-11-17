# Advanced AI-Powered Beauty Shopping Assistant

**A Hybrid RAG & Tool-Calling AI Agent for Intelligent Beauty Product Discovery**

An AI-powered beauty shopping assistant designed to help users discover, search, and compare skincare, sunscreen, makeup, and personal care products through natural language conversations.

The system combines structured database queries, semantic retrieval, and an LLM-powered agent to deliver context-aware product recommendations based on user preferences and product attributes.

## Key Features

- **Conversational AI Agent:** Understands natural language requests and maintains context across multiple conversation turns.
- **Hybrid RAG Retrieval:** Combines structured SQL filtering with semantic vector search to retrieve relevant products.
- **Deterministic Intent Extraction:** Extracts user intent and product requirements while preserving relevant preferences from conversation history.
- **Tool Calling:** Uses controlled application tools to retrieve product information instead of relying exclusively on generated model knowledge.
- **Structured Product Search:** Supports filtering by attributes such as category, brand, skin type, and minimum SPF.
- **Conversation Persistence:** Stores conversation sessions and message history in PostgreSQL.
- **Local LLM Integration:** Uses Ollama to run language models locally.

## System Architecture

The application follows a modular architecture:

1. **API Layer — FastAPI**
   - Exposes chat endpoints.
   - Handles incoming requests and session management.

2. **Agent Layer**
   - Processes user messages.
   - Extracts intent and product requirements.
   - Maintains conversational context.
   - Executes application tools when product retrieval is needed.

3. **Retrieval Layer — Hybrid RAG**
   - SQL-based filtering through PostgreSQL.
   - Semantic retrieval through ChromaDB.
   - Combines structured and semantic results.

4. **Database Layer — PostgreSQL**
   - Stores products, brands, categories, product sources, conversations, and chat messages.

5. **LLM Layer — Ollama**
   - Runs the local language model.
   - Handles conversational responses and intent extraction.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| LLM Runtime | Ollama |
| Language Model | Qwen 2.5 |
| Embedding Model | BGE-M3 |
| Relational Database | PostgreSQL |
| Vector Database | ChromaDB |
| ORM | SQLAlchemy |
| Data Validation | Pydantic |
| HTTP Client | HTTPX |
| Containerization | Docker, Docker Compose |

## Project Structure

```text
advanced-rag-agent/
│
├── app/
│   ├── agent/
│   │   ├── agent.py
│   │   ├── intent_extractor.py
│   │   ├── normalizers.py
│   │   ├── ollama_client.py
│   │   ├── tool_definitions.py
│   │   └── tools.py
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── chat.py
│   │       └── product_sources.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   └── models.py
│   │
│   ├── rag/
│   │   └── vector_store.py
│   │
│   ├── schemas/
│   └── services/
│       └── conversation_repo.py
│
├── storage/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- Ollama
- Qwen 2.5 model
- BGE-M3 embedding model

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd advanced-rag-agent
```

### 2. Create a Virtual Environment

```bash
uv venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
uv pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Update the environment variables according to the application configuration, including database connection settings and Ollama model endpoints.

### 5. Start PostgreSQL

```bash
docker compose up -d
```

### 6. Start Ollama

Make sure Ollama is running and the required models are available:

```bash
ollama pull qwen2.5:3b
ollama pull bge-m3
```

Configure the Ollama endpoint in the application environment.

### 7. Run the API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:

```text
http://localhost:8000
```

FastAPI interactive documentation:

```text
http://localhost:8000/docs
```

## API Usage

### Chat Endpoint

`POST /api/chat`

Example request:

```json
{
  "message": "I have oily skin. Recommend a sunscreen with SPF 50 or higher."
}
```

Example response structure:

```json
{
  "response": "Here are some sunscreen recommendations...",
  "session_id": "your-session-id"
}
```

The returned session ID can be reused to continue an existing conversation and preserve conversational context.

## Current Development Status

- [x] FastAPI backend initialization
- [x] PostgreSQL database integration
- [x] Product and conversation data models
- [x] ChromaDB vector store integration
- [x] BGE-M3 embedding integration
- [x] Ollama LLM integration
- [x] Product search tools
- [x] Hybrid SQL and semantic retrieval
- [x] Deterministic intent extraction
- [x] Conversational context handling
- [x] Chat API endpoint
- [x] Persistent conversation and message history
- [ ] Automated test suite with Pytest
- [ ] Complete Docker-based application deployment
- [ ] React-based chat interface
- [ ] Expanded product catalog and verified product sources

## Future Improvements

- Expand the product catalog across skincare, makeup, haircare, and personal care.
- Improve retrieval ranking and recommendation relevance.
- Add automated unit and integration tests.
- Containerize the complete application.
- Build a React-based conversational shopping interface.
- Improve product provenance and source verification.
- Add product comparison and personalized recommendation workflows.

---

**Project Focus:** AI Agents, Retrieval-Augmented Generation (RAG), Hybrid Search, LLM Tool Calling, Backend Engineering, and Conversational AI.