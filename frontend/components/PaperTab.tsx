"use client"

import { useState } from "react"
import { Paper, Citation, PaperCandidate, selectPaper } from "@/lib/api"
import { Plus, Loader2, X, ChevronRight } from "lucide-react"

interface PaperTabProps {
	paper: Paper
	onGraphUpdate?: () => void
}

const PaperTab = ({ paper, onGraphUpdate }: PaperTabProps) => {
	const [addingCitation, setAddingCitation] = useState<string | null>(null)
	const [addedCitations, setAddedCitations] = useState<Set<string>>(new Set())
	const [candidates, setCandidates] = useState<{ citation: Citation; options: PaperCandidate[] } | null>(null)

	const handleAddCitation = async (citation: Citation) => {
		const citationKey = citation.arxiv_id || citation.title
		setAddingCitation(citationKey)
		setCandidates(null)
		try {
			const response = await selectPaper(citation.arxiv_id || citation.title, paper.id)
			if (response.papers_added?.length > 0) {
				setAddedCitations(prev => new Set(prev).add(citationKey))
				onGraphUpdate?.()
			} else if (response.paper_candidates?.length > 0) {
				setCandidates({ citation, options: response.paper_candidates })
			}
		} catch (error) {
			console.error("Failed to add citation:", error)
		} finally {
			setAddingCitation(null)
		}
	}

	const handleSelectCandidate = async (candidate: PaperCandidate) => {
		setAddingCitation(candidate.arxiv_id)
		try {
			const response = await selectPaper(candidate.arxiv_id, paper.id)
			if (response.papers_added?.length > 0) {
				if (candidates?.citation) {
					const citationKey = candidates.citation.arxiv_id || candidates.citation.title
					setAddedCitations(prev => new Set(prev).add(citationKey))
				}
				onGraphUpdate?.()
			}
		} catch (error) {
			console.error("Failed to add paper:", error)
		} finally {
			setAddingCitation(null)
			setCandidates(null)
		}
	}

	const formatDate = (dateStr: string) => {
		return new Date(dateStr).toLocaleDateString("en-US", {
			year: "numeric",
			month: "long",
			day: "numeric"
		})
	}

	return (
		<div className="h-full flex flex-col bg-[#1e1e1e]">
			<div className="flex-1 overflow-y-auto p-6">
				<article className="prose prose-invert prose-sm max-w-none">
					<h1 className="text-xl font-bold text-white/90 mb-4">{paper.title}</h1>

					<div className="flex flex-wrap gap-2 mb-4">
						<span className="px-2 py-0.5 bg-white/10 text-white/60 text-xs rounded-full">
							{formatDate(paper.published)}
						</span>
					</div>

					<section className="mb-6">
						<h2 className="text-sm font-semibold text-white/70 uppercase tracking-wide mb-2">Authors</h2>
						<p className="text-white/80 text-sm">{paper.authors.join(", ")}</p>
					</section>

					<section className="mb-6">
						<h2 className="text-sm font-semibold text-white/70 uppercase tracking-wide mb-2">Abstract</h2>
						<p className="text-white/80 text-sm leading-relaxed whitespace-pre-wrap">{paper.summary}</p>
					</section>
					{paper.key_concepts && paper.key_concepts.length > 0 && (
						<section className="mb-6">
							<h2 className="text-sm font-semibold text-white/70 uppercase tracking-wide mb-2">
								Key Concepts
							</h2>
							<div className="flex flex-wrap gap-2">
								{paper.key_concepts.map((concept, idx) => (
									<span
										key={idx}
										className="px-2 py-1 bg-purple-500/20 text-purple-300 text-xs rounded-md"
									>
										{concept}
									</span>
								))}
							</div>
						</section>
					)}
					<section className="mb-6">
						<h2 className="text-sm font-semibold text-white/70 uppercase tracking-wide mb-2">Links</h2>
						<div className="flex gap-4">
							<a
								href={`https://arxiv.org/abs/${paper.id}`}
								target="_blank"
								rel="noopener noreferrer"
								className="text-[#4A9D9A] hover:underline text-sm"
							>
								View on arXiv
							</a>
						</div>
					</section>
					{paper.citations && paper.citations.length > 0 && (
						<section className="mb-6">
							<h2 className="text-sm font-semibold text-white/70 uppercase tracking-wide mb-3">
								References ({paper.citations.length})
							</h2>
							{candidates && (
								<div className="mb-4 p-3 bg-white/5 rounded-lg border border-white/10">
									<div className="flex items-center justify-between mb-2">
										<span className="text-white/60 text-xs">Select the correct paper:</span>
										<button
											onClick={() => setCandidates(null)}
											className="text-white/40 hover:text-white/60"
										>
											<X className="w-4 h-4" />
										</button>
									</div>
									<div className="space-y-1">
										{candidates.options.map(candidate => (
											<button
												key={candidate.arxiv_id}
												onClick={() => handleSelectCandidate(candidate)}
												disabled={addingCitation === candidate.arxiv_id}
												className="w-full flex items-center gap-2 px-2 py-1.5 rounded text-sm text-left hover:bg-white/5"
											>
												{addingCitation === candidate.arxiv_id ? (
													<Loader2 className="w-3.5 h-3.5 animate-spin text-[#4A9D9A]" />
												) : (
													<ChevronRight className="w-3.5 h-3.5 text-[#4A9D9A]" />
												)}
												<div className="flex-1 min-w-0">
													<div className="text-white/80 line-clamp-1">{candidate.title}</div>
													<div className="text-white/40 text-xs">
														{candidate.arxiv_id} ·{" "}
														{candidate.authors.slice(0, 2).join(", ")} · {candidate.year}
													</div>
												</div>
											</button>
										))}
									</div>
								</div>
							)}
							<div className="space-y-1.5">
								{paper.citations.map((citation, idx) => {
									const citationKey = citation.arxiv_id || citation.title
									const isAdding = addingCitation === citationKey
									const isAdded = addedCitations.has(citationKey)
									return (
										<button
											key={idx}
											onClick={() => handleAddCitation(citation)}
											disabled={isAdding || isAdded}
											className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-sm text-left transition-colors ${
												isAdded ? "opacity-50" : "hover:bg-white/5"
											}`}
										>
											<div className="text-[#4A9D9A] flex-shrink-0">
												{isAdding ? (
													<Loader2 className="w-3.5 h-3.5 animate-spin" />
												) : (
													<Plus className="w-3.5 h-3.5" />
												)}
											</div>
											<div className="flex-1 min-w-0">
												<span className="text-white/80 line-clamp-1">{citation.title}</span>
												{citation.arxiv_id && (
													<span className="text-[#4A9D9A] text-xs font-mono ml-2">
														{citation.arxiv_id}
													</span>
												)}
											</div>
										</button>
									)
								})}
							</div>
						</section>
					)}
				</article>
			</div>
		</div>
	)
}

export default PaperTab
