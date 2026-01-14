# Research Paper Connection Agent

A full-stack application for discovering and visualizing relationships between academic papers from arXiv. Chat with an AI agent using the Tavily APIs (search, extract, crawl, map) and AWS Bedrock using Opus 4.5 to add papers, find citations, and explore connection graphs.

There is no authentication, we are persisting chat conversations and uploaded papers and edges. This was necessary because the goal of the application is to use the agents to build a knowledge graph of connected papers and to be able to find connections between papers you might not have otherwise found. Without persistence, your chat and graph is gone on shut down and refresh.

Papers are nodes, citations/references or semantic links that are found are your edges.

## Using

-   Python 3.10+
-   Node.js 18+
-   AWS account with Bedrock access (Claude Opus 4.5)
-   Tavily API key
-   Supabase project

---

## Backend

The backend uses LangGraph to orchestrate a pipeline of AI agents. The workflow is defined in `backend/graph.py`:

1. **Router Agent** (`agents/router.py`) - Classifies user intent into: `add_paper`, `search_paper`, `find_related`, `find_connections`, `extract`, `crawl`, `map`, or `question`

2. **Specialized Agents** - Each handles a specific task:

    - `ingest` - Fetches papers from arXiv
    - `search` - Searches for papers
    - `citation` - Finds and creates citation links
    - `extract` - Extracts knowledge from PDFs
    - `crawl` - Crawls web pages for paper references
    - `map` - Maps URLs from pages
    - `related` - Finds related papers
    - `answer` - Answers general questions

3. **Synthesis Agent** (`agents/synthesis.py`) - Generates final response and builds Cytoscape graph data

State flows through `ResearchGraphState` (defined in `backend/state.py`) which accumulates papers, edges, and responses.

Uses AWS Bedrock with Claude Opus 4.5 (`us.anthropic.claude-opus-4-5-20251101-v1:0`).

### Data Models

Core models in `backend/models.py`:

-   `Paper` - Academic paper with id (arXiv ID), title, authors, summary, citations
-   `Edge` - Simple connection between papers (source_id, target_id)
-   `GraphData` - Collection of nodes (papers) and edges

### LLM Integration

All LLM calls go through `agents/base.py`:

-   `invoke_bedrock(prompt)` - Text-only prompts
-   `invoke_bedrock_with_pdf(prompt, pdf_bytes)` - Document understanding

---

### Frontend

Next.js 16 app with React 19. Key components:

-   `components/GraphView.tsx` - Cytoscape graph visualization
-   `components/Chat.tsx` - Chat interface for interacting with agents
-   `components/TabbedPane.tsx` - Paper details in tabs
-   `lib/api.ts` - API client for backend communication

## Setup

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
```

Create `backend/.env`:

Will give you api keys on request if you want to play around with it.

```
TAVILY_API_KEY=your_tavily_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_DEFAULT_REGION=us-east-1
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

Run the API:

```bash
uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```
