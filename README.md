# Research Paper Connection Agent

A full-stack application for discovering and visualizing relationships between academic papers from arXiv. Chat with an AI agent using the Tavily APIs (search, extract, crawl, map) and AWS Bedrock using Opus 4.5 to add papers, find citations, and explore connection graphs.

There is no authentication, we are persisting chat conversations and uploaded papers and edges. This was necessary because the goal of the application is to use the agents to build a knowledge graph of connected papers and to be able to find connections between papers you might not have otherwise found. Without persistence, obviously your chat and graph is gone on refresh or shut down
Papers are nodes, citations/references or semantic links that are found are your edges.

## Using

-   Python 3.10+
-   Node.js 18+
-   AWS account with Bedrock access (Claude Opus 4.5)
-   Tavily API key
-   Supabase project

---

## Backend

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER MESSAGE                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          ROUTER AGENT                                    │
│                    (Intent Classification)                               │
│                                                                          │
│  Classifies user intent into one of 8 categories using Claude LLM       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────┬───────────┬───┴───┬───────────┬───────────┬─────────┐
        ▼           ▼           ▼       ▼           ▼           ▼         ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ INGEST  │ │ SEARCH  │ │ RELATED │ │ ANSWER  │ │ EXTRACT │ │  CRAWL  │
   │  AGENT  │ │  AGENT  │ │  AGENT  │ │  AGENT  │ │  AGENT  │ │  AGENT  │
   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
        │           │           │           │           │           │
        ▼           │           │           │           │           │
   ┌─────────┐      │           │           │           │           │
   │CITATION │      │           │           │           │           │
   │  AGENT  │      │           │           │           │           │
   └────┬────┘      │           │           │           │           │
        │           │           │           │           │           │
        └───────────┴───────────┴─────┬─────┴───────────┴───────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         SYNTHESIS AGENT                                  │
│              (Build Response + Format Graph for UI)                      │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      KNOWLEDGE GRAPH + RESPONSE                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Agent Purposes & Tavily API Usage

### 1. Router Agent

**Purpose:** Intent classification - determines which specialized agent should handle the user's request.

**How it works:**

-   Extracts arXiv IDs from message using regex (e.g., `2401.12345`)
-   If arXiv ID found → routes to Ingest Agent
-   Otherwise → uses Claude LLM to classify into 8 intents

**No Tavily API used** - Uses Claude Bedrock for classification.

---

### 2. Ingest Agent

**Purpose:** Add papers to the knowledge graph by fetching from arXiv.

**Tavily API:** `tavily.search()` (fallback when paper name search needed)

**How it works:**

1. If arXiv ID provided → fetches directly from arXiv API
2. If paper name provided → searches arXiv by name
3. Extracts key concepts using Claude
4. Extracts citations from PDF using Claude vision
5. Stores paper in Supabase

**Example queries:**

-   "Add paper 2401.12345"
-   "Add the Attention Is All You Need paper"

---

### 3. Search Agent

**Purpose:** Discover new papers on a topic using web search.

**Tavily API:** `tavily.search(query, include_domains=["arxiv.org"])`

**How it works:**

1. Extracts search topic from user message
2. Searches for arXiv papers using Tavily Search API
3. Returns paper candidates for user to select

**Example queries:**

-   "Search for papers about transformer architectures"
-   "Find recent papers on large language models"

---

### 4. Related Papers Agent

**Purpose:** Find papers that cite or are related to a specific paper.

**Tavily API:** `tavily.search()` with citation-focused query

**How it works:**

1. Extracts paper title from message
2. Matches against existing papers in collection (for source tracking)
3. Searches for citing/related papers
4. Filters out papers already in collection

**Example queries:**

-   "Find papers related to BERT"
-   "What papers cite Attention Is All You Need?"

---

### 5. Citation Agent

**Purpose:** Find connections between papers in the collection based on shared concepts.

**No Tavily API used** - Works with existing collection.

**How it works:**

1. Compares key concepts between papers
2. Creates edges for papers with shared concepts
3. Stores edges in Supabase

**Example queries:**

-   "Find connections between my papers"
-   Automatically runs after adding a new paper

---

### 6. Answer Agent

**Purpose:** Answer research questions using paper context and web search.

**Tavily API:** `tavily.search()` for additional context

**How it works:**

1. Builds context from papers in collection
2. Searches web for additional information
3. Uses Claude to generate comprehensive answer

**Example queries:**

-   "What are the key differences between BERT and GPT?"
-   "How do transformers work?"

---

### 7. Extract Agent

**Purpose:** Extract and summarize content from any URL.

**Tavily API:** `tavily.extract(urls)`

**How it works:**

1. Extracts URL from user message
2. Uses Tavily Extract to fetch page content
3. Summarizes content using Claude
4. Detects arXiv links and offers to add papers

**Example queries:**

-   "Extract content from https://arxiv.org/abs/2401.12345"
-   "Summarize this article: https://example.com/research"

---

### 8. Crawl Agent

**Purpose:** Discover papers by crawling websites.

**Tavily API:** `tavily.crawl(url, instructions)`

**How it works:**

1. Extracts target URL from message
2. Crawls site looking for arXiv paper links
3. Extracts paper candidates from crawled pages

**Example queries:**

-   "Crawl this author's page for papers"
-   "Find papers from https://researcher.github.io"

---

### 9. Map Agent

**Purpose:** Map site structure to discover available papers.

**Tavily API:** `tavily.map(url)`

**How it works:**

1. Maps all URLs on a site
2. Filters for arXiv paper links (/abs/, /pdf/)
3. Returns discovered paper candidates

**Example queries:**

-   "Map arxiv.org/list/cs.AI/recent"
-   "What papers are available on this site?"

---

### 10. Synthesis Agent

**Purpose:** Build final response and format graph for frontend.

**No Tavily API used** - Aggregates results.

**How it works:**

1. Retrieves current graph state from storage
2. Formats graph for Cytoscape visualization
3. Combines response parts into final message

---

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

Run tests:

```bash
cd backend
pytest -v
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

---

### Improvements

Creating better semantic understanding when finding connections among papers. Right now, when we use the ingest agent, the LLM extracts out 3-5 key concepts from the papers title and abstract. These are used to compare amongst added papers so there is:

1. No semantic understanding when finding links.
2. Depends on LLM consistency of the key concept tags.
