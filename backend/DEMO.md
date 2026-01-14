# Research Paper Knowledge Graph - Agent Orchestration Demo

## System Overview

This system uses **LangGraph** to orchestrate multiple specialized agents that build and query a knowledge graph of research papers. The agents collaborate through a shared state, with each agent handling specific tasks and passing results to the next.

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
- Extracts arXiv IDs from message using regex (e.g., `2401.12345`)
- If arXiv ID found → routes to Ingest Agent
- Otherwise → uses Claude LLM to classify into 8 intents

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
- "Add paper 2401.12345"
- "Add the Attention Is All You Need paper"

---

### 3. Search Agent
**Purpose:** Discover new papers on a topic using web search.

**Tavily API:** `tavily.search(query, include_domains=["arxiv.org"])`

**How it works:**
1. Extracts search topic from user message
2. Searches for arXiv papers using Tavily Search API
3. Returns paper candidates for user to select

**Example queries:**
- "Search for papers about transformer architectures"
- "Find recent papers on large language models"

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
- "Find papers related to BERT"
- "What papers cite Attention Is All You Need?"

---

### 5. Citation Agent
**Purpose:** Find connections between papers in the collection based on shared concepts.

**No Tavily API used** - Works with existing collection.

**How it works:**
1. Compares key concepts between papers
2. Creates edges for papers with shared concepts
3. Stores edges in Supabase

**Example queries:**
- "Find connections between my papers"
- Automatically runs after adding a new paper

---

### 6. Answer Agent
**Purpose:** Answer research questions using paper context and web search.

**Tavily API:** `tavily.search()` for additional context

**How it works:**
1. Builds context from papers in collection
2. Searches web for additional information
3. Uses Claude to generate comprehensive answer

**Example queries:**
- "What are the key differences between BERT and GPT?"
- "How do transformers work?"

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
- "Extract content from https://arxiv.org/abs/2401.12345"
- "Summarize this article: https://example.com/research"

---

### 8. Crawl Agent
**Purpose:** Discover papers by crawling websites.

**Tavily API:** `tavily.crawl(url, instructions)`

**How it works:**
1. Extracts target URL from message
2. Crawls site looking for arXiv paper links
3. Extracts paper candidates from crawled pages

**Example queries:**
- "Crawl this author's page for papers"
- "Find papers from https://researcher.github.io"

---

### 9. Map Agent
**Purpose:** Map site structure to discover available papers.

**Tavily API:** `tavily.map(url)`

**How it works:**
1. Maps all URLs on a site
2. Filters for arXiv paper links (/abs/, /pdf/)
3. Returns discovered paper candidates

**Example queries:**
- "Map arxiv.org/list/cs.AI/recent"
- "What papers are available on this site?"

---

### 10. Synthesis Agent
**Purpose:** Build final response and format graph for frontend.

**No Tavily API used** - Aggregates results.

**How it works:**
1. Retrieves current graph state from storage
2. Formats graph for Cytoscape visualization
3. Combines response parts into final message

---

## Demo Script (3-5 minutes)

### Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Demo Flow

#### Part 1: Adding Papers (1 min)
Show how papers are added to the graph.

```
User: "Add paper 1706.03762"
→ Router detects arXiv ID → Ingest Agent
→ Fetches "Attention Is All You Need" from arXiv
→ Extracts key concepts: transformers, attention, neural networks
→ Extracts citations from PDF
→ Graph now has 1 node
```

```
User: "Add the BERT paper"
→ Router → Ingest Agent
→ Searches arXiv by name → Returns candidates
→ User selects → Paper added
→ Citation Agent finds shared concept: "transformers"
→ Graph now has 2 nodes + 1 edge
```

#### Part 2: Discovering Papers with Tavily (1 min)
Show Tavily Search and Crawl capabilities.

```
User: "Search for papers about vision transformers"
→ Router → Search Agent
→ Tavily Search API: "vision transformers research paper" + arxiv.org domain
→ Returns 5 paper candidates
→ User can select to add
```

```
User: "Crawl this author page: https://arxiv.org/search/?searchtype=author&query=Vaswani"
→ Router → Crawl Agent
→ Tavily Crawl API: discovers paper links
→ Extracts arXiv IDs from crawled content
→ Returns paper candidates
```

#### Part 3: Extracting Content (30 sec)
Show Tavily Extract capability.

```
User: "Extract https://arxiv.org/abs/2010.11929"
→ Router → Extract Agent
→ Tavily Extract API: fetches page content
→ Claude summarizes the paper
→ Detects arXiv ID, offers to add
```

#### Part 4: Finding Connections (1 min)
Show knowledge graph building.

```
User: "Find connections between my papers"
→ Router → Citation Agent
→ Compares key concepts across all papers
→ Creates edges for shared concepts
→ "Found 3 connections based on shared concepts"
```

```
User: "Find papers related to BERT"
→ Router → Related Agent
→ Tavily Search for citing papers
→ Filters out papers already in collection
→ Returns new paper candidates
```

#### Part 5: Asking Questions (30 sec)
Show the Answer Agent.

```
User: "What's the relationship between BERT and GPT?"
→ Router → Answer Agent
→ Builds context from papers in collection
→ Tavily Search for additional info
→ Claude generates comprehensive answer
```

---

## Tavily API Summary

| Agent | Tavily API | Purpose |
|-------|------------|---------|
| Search Agent | `search()` | Find papers on a topic |
| Related Agent | `search()` | Find citing/related papers |
| Answer Agent | `search()` | Get additional context for Q&A |
| Extract Agent | `extract()` | Get content from any URL |
| Crawl Agent | `crawl()` | Discover papers by crawling sites |
| Map Agent | `map()` | Map site structure for papers |

---

## Key Demo Points

1. **Agent Orchestration**: Show how Router directs to specialized agents
2. **Shared State**: Agents pass data through LangGraph state
3. **Automatic Connections**: Citation Agent runs after paper ingestion
4. **Tavily Integration**: 4 different APIs for different discovery methods
5. **Knowledge Graph**: Visual representation of papers and connections

---

## API Endpoints for Demo

```bash
# Add paper by arXiv ID
POST /papers {"arxiv_id": "1706.03762"}

# Chat interface (uses full pipeline)
POST /chat {"message": "Search for transformer papers"}

# Get graph for visualization
GET /graph/cytoscape

# See all papers
GET /papers
```
