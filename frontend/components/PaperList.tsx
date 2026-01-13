import { Paper } from "@/lib/api"

interface PaperListProps {
	papers: Paper[]
	onPaperClick?: (paper: Paper) => void
	selectedPaperId?: string
}

const PaperList = ({ papers, onPaperClick, selectedPaperId }: PaperListProps) => {
	if (papers.length === 0) {
		return (
			<div className="p-4 text-center text-zinc-500">
				<p>No papers yet.</p>
				<p className="text-sm mt-1">Add papers via the chat.</p>
			</div>
		)
	}

	return (
		<div className="divide-y dark:divide-zinc-800">
			{papers.map(paper => (
				<div
					key={paper.id}
					onClick={() => onPaperClick?.(paper)}
					className={`p-3 cursor-pointer hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors ${
						selectedPaperId === paper.id ? "bg-blue-50 dark:bg-blue-900/20 border-l-2 border-blue-500" : ""
					}`}
				>
					<h3 className="font-medium text-sm text-zinc-900 dark:text-zinc-100 line-clamp-2">{paper.title}</h3>
					<p className="text-xs text-zinc-500 mt-1">
						{paper.authors.slice(0, 2).join(", ")}
						{paper.authors.length > 2 && " et al."}
					</p>
					<div className="flex flex-wrap gap-1 mt-2">
						{paper.key_concepts.slice(0, 3).map((concept, idx) => (
							<span
								key={idx}
								className="px-2 py-0.5 text-xs bg-zinc-200 dark:bg-zinc-700 rounded-full text-zinc-700 dark:text-zinc-300"
							>
								{concept}
							</span>
						))}
					</div>
					<p className="text-xs text-zinc-400 mt-1">{paper.id}</p>
				</div>
			))}
		</div>
	)
}

export default PaperList
