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

## Usage

There will be an exclusive chip selection of the main research categories on arxiv that shows sample prompts relating to the selected category and

-   Type an arXiv ID (e.g., `2401.12345`) or paper title to add papers
-   Ask questions like "Find papers related to transformers"
-   Click nodes in the graph to view paper details
-   Use the sidebar to browse added papers
