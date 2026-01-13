import { ArxivCategory } from "./constants"

export interface Prompt {
	id: string
	text: string
}

// Prompts aligned with backend agents:
// - Ingest: Add papers from arXiv
// - Citation: Find connections between papers
// - Answer: Ask questions about papers

export const PROMPTS_BY_CATEGORY: Record<ArxivCategory, Prompt[]> = {
	cs: [
		{ id: "cs1", text: "Add the Attention Is All You Need paper" },
		{ id: "cs2", text: "Find connections between my papers" },
		{ id: "cs3", text: "What are the key innovations in transformers?" }
	],
	econ: [
		{ id: "econ1", text: "Add papers on behavioral economics" },
		{ id: "econ2", text: "Find connections between my papers" },
		{ id: "econ3", text: "Explain game theory fundamentals" }
	],
	math: [
		{ id: "math1", text: "Add papers on topology" },
		{ id: "math2", text: "Find connections between my papers" },
		{ id: "math3", text: "What is the Riemann hypothesis?" }
	],
	physics: [
		{ id: "ph1", text: "Add papers on quantum computing" },
		{ id: "ph2", text: "Find connections between my papers" },
		{ id: "ph3", text: "What is quantum entanglement?" }
	],
	bio: [
		{ id: "bio1", text: "Add papers on protein folding" },
		{ id: "bio2", text: "Find connections between my papers" },
		{ id: "bio3", text: "How does AlphaFold predict structure?" }
	],
	finance: [
		{ id: "fin1", text: "Add papers on portfolio optimization" },
		{ id: "fin2", text: "Find connections between my papers" },
		{ id: "fin3", text: "Explain modern risk modeling" }
	],
	stat: [
		{ id: "st1", text: "Add the Bayesian optimization paper" },
		{ id: "st2", text: "Find connections between my papers" },
		{ id: "st3", text: "Explain regularization techniques" }
	]
}
