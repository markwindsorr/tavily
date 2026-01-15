"use client"

import { useState } from "react"
import { Paper, Reference, selectPaper } from "@/lib/api"
import { Plus, Loader2 } from "lucide-react"

interface PaperTabProps {
	paper: Paper
	onGraphUpdate?: () => void
}

const PaperTab = ({ paper, onGraphUpdate }: PaperTabProps) => {
	const [addingReference, setAddingReference] = useState<string | null>(null)
	const [addedReferences, setAddedReferences] = useState<Set<string>>(new Set())

	const handleAddReference = async (reference: Reference) => {
		setAddingReference(reference.arxiv_id)
		try {
			const response = await selectPaper(reference.arxiv_id, paper.id)
			if (response.papers_added?.length > 0) {
				setAddedReferences(prev => new Set(prev).add(reference.arxiv_id))
				onGraphUpdate?.()
			}
		} catch (error) {
			console.error("Failed to add reference:", error)
		} finally {
			setAddingReference(null)
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
					{paper.references && paper.references.length > 0 && (
						<section className="mb-6">
							<h2 className="text-sm font-semibold text-white/70 uppercase tracking-wide mb-3">
								References ({paper.references.length})
							</h2>
							<div className="space-y-1.5">
								{paper.references.map((reference, idx) => {
									const isAdding = addingReference === reference.arxiv_id
									const isAdded = addedReferences.has(reference.arxiv_id)
									return (
										<button
											key={idx}
											onClick={() => handleAddReference(reference)}
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
												<span className="text-white/80 line-clamp-1">{reference.title}</span>
												<span className="text-[#4A9D9A] text-xs font-mono ml-2">
													{reference.arxiv_id}
												</span>
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
