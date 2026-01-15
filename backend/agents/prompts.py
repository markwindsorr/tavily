"""Prompt constants for all agents."""

# =============================================================================
# Router Agent Prompts
# =============================================================================

ROUTER_PROMPT = """You are a router agent for a research paper connection system.
Classify the user's intent into one of these categories:

1. "add_paper" - User wants to add a specific paper by name or title
2. "search_paper" - User wants to search/discover papers on a topic or keyword (uses Tavily Search)
3. "find_related" - User wants to find papers related to or citing a specific paper (uses Tavily Search)
4. "find_connections" - User wants to find connections between papers already in their collection
5. "question" - User has a question about papers or research (uses Tavily Search)
6. "extract" - User wants to extract/summarize content from a specific URL (uses Tavily Extract)
7. "crawl" - User wants to discover papers by crawling a site or author page (uses Tavily Crawl)
8. "map" - User wants to explore/map what papers are available on a site or category (uses Tavily Map)

Respond with ONLY the category name, nothing else.

User message: {message}
"""

# =============================================================================
# Ingest Agent Prompts
# =============================================================================

CONCEPT_EXTRACTION_PROMPT = """Extract 3-5 key concepts/topics from this research paper abstract.
Return them as a comma-separated list. Focus on the main technical contributions and methods.

Title: {title}
Abstract: {abstract}

Key concepts (comma-separated):"""

PAPER_NAME_EXTRACTION_PROMPT = """Extract the paper name or topic the user wants to add from this message.
Return ONLY the paper name/title or search query, nothing else.

User message: {message}

Paper name:"""

# =============================================================================
# Answer Agent Prompts
# =============================================================================

ANSWER_PROMPT = """You are a research assistant helping with questions about academic papers.

User's papers in their collection:
{papers_context}

Connections between papers:
{edges_context}

User's question: {question}

Relevant search results from the web:
{search_results}

Provide a helpful, accurate answer based on the papers in their collection and the search results.
If the question is about comparing papers, focus on their key contributions and differences.
Keep the response concise but informative (2-4 paragraphs).
"""

# =============================================================================
# Extract Agent Prompts
# =============================================================================

EXTRACT_URL_EXTRACTION_PROMPT = """Extract the URL the user wants to analyze from this message.
Return ONLY the URL, nothing else.

User message: {message}

URL:"""

SUMMARIZE_CONTENT_PROMPT = """Summarize the following web page content in a clear, informative way.
Focus on the main points, especially if it's about research or academic content.
Keep the summary concise but comprehensive (2-3 paragraphs).

Content:
{content}

Summary:"""

# =============================================================================
# Related Papers Agent Prompts
# =============================================================================

PAPER_TITLE_EXTRACTION_PROMPT = """Extract the paper title from this user message.
The user wants to find papers related to or cited by this paper.
Return ONLY the paper title or search terms, nothing else.

User message: {message}

Paper title:"""

RELATED_REFERENCE_EXTRACTION_PROMPT = """Analyze the references/bibliography section of this research paper PDF.

Extract up to 15 cited papers that have arXiv IDs.

Return a JSON array with objects containing:
- "title": the paper title
- "arxiv_id": the arXiv ID (format: XXXX.XXXXX, e.g., 1706.03762)
- "author": the first author's last name

Example output:
[{"title": "Attention Is All You Need", "arxiv_id": "1706.03762", "author": "Vaswani"}]

IMPORTANT:
- Look carefully for arXiv IDs - they often appear as "arXiv:1706.03762" or "arxiv.org/abs/1706.03762"
- ONLY include references that have a clear arXiv ID
- Return ONLY the JSON array, no other text"""

# =============================================================================
# Crawl Agent Prompts
# =============================================================================

CRAWL_URL_EXTRACTION_PROMPT = """Extract the URL or site the user wants to crawl/explore from this message.
If the user mentions an author name, return a search URL like: https://arxiv.org/search/?searchtype=author&query=AUTHOR_NAME
If the user mentions a topic or category, return a listing URL like: https://arxiv.org/list/cs.AI/recent
If the user provides a direct URL, return that URL.

User message: {message}

Return ONLY the URL, nothing else."""

CRAWL_INSTRUCTIONS_PROMPT = """Based on the user's request, generate specific instructions for crawling to find research papers.

User message: {message}

Return 1-2 sentences of crawl instructions focused on finding arXiv paper links."""