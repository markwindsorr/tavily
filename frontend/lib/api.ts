const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export interface Citation {
	title: string
	arxiv_id?: string
	author?: string
}

export interface Paper {
	id: string
	title: string
	authors: string[]
	summary: string
	published: string
	pdf_url: string
	key_concepts: string[]
	citations: Citation[]
}

export interface Edge {
	id: string
	source_id: string
	target_id: string
}

export interface PaperCandidate {
	arxiv_id: string
	title: string
	authors: string[]
	year: number
	source_paper_id?: string
}

export interface ChatResponse {
	message: string
	graph_updated: boolean
	papers_added: string[]
	paper_candidates: PaperCandidate[]
}

export interface CytoscapeGraph {
	elements: Array<{
		data: Record<string, unknown>
	}>
}

export const getPapers = async (): Promise<Paper[]> => {
	const res = await fetch(`${API_BASE}/papers`)
	if (!res.ok) throw new Error("Failed to fetch papers")
	return res.json()
}

export const getCytoscapeGraph = async (): Promise<CytoscapeGraph> => {
	const res = await fetch(`${API_BASE}/graph/cytoscape`)
	if (!res.ok) throw new Error("Failed to fetch graph")
	return res.json()
}

export const sendChatMessage = async (message: string): Promise<ChatResponse> => {
	const res = await fetch(`${API_BASE}/chat`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ message })
	})
	if (!res.ok) throw new Error("Failed to send message")
	return res.json()
}

export const getChatHistory = async (): Promise<Array<{ role: string; content: string; created_at: string }>> => {
	const res = await fetch(`${API_BASE}/chat/history`)
	if (!res.ok) throw new Error("Failed to fetch chat history")
	return res.json()
}

export const clearChatHistory = async (): Promise<void> => {
	const res = await fetch(`${API_BASE}/chat/history`, { method: "DELETE" })
	if (!res.ok) throw new Error("Failed to clear chat history")
}

export const selectPaper = async (arxivId: string, sourcePaperId?: string): Promise<ChatResponse> => {
	const res = await fetch(`${API_BASE}/papers/select`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ arxiv_id: arxivId, source_paper_id: sourcePaperId })
	})
	if (!res.ok) throw new Error("Failed to select paper")
	return res.json()
}

export const deletePaper = async (paperId: string): Promise<void> => {
	const res = await fetch(`${API_BASE}/papers/${encodeURIComponent(paperId)}`, { method: "DELETE" })
	if (!res.ok) throw new Error("Failed to delete paper")
}

export const deleteEdge = async (edgeId: string): Promise<void> => {
	const res = await fetch(`${API_BASE}/edges/${encodeURIComponent(edgeId)}`, { method: "DELETE" })
	if (!res.ok) throw new Error("Failed to delete edge")
}
