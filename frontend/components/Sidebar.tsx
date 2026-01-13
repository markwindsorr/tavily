"use client"

import { useState, useEffect, useRef } from "react"
import { Paper } from "@/lib/api"
import { Trash2, Loader2 } from "lucide-react"

interface SidebarProps {
	papers: Paper[]
	onPaperClick?: (paper: Paper) => void
	onDeletePaper?: (paperId: string) => void
	selectedPaperId?: string
	deletingPaperId?: string | null
}

interface ContextMenuState {
	x: number
	y: number
	paperId: string
}

const Sidebar = ({ papers, onPaperClick, onDeletePaper, selectedPaperId, deletingPaperId }: SidebarProps) => {
	const [contextMenu, setContextMenu] = useState<ContextMenuState | null>(null)
	const contextMenuRef = useRef<HTMLDivElement>(null)

	useEffect(() => {
		const handleClickOutside = (e: MouseEvent) => {
			if (contextMenuRef.current && !contextMenuRef.current.contains(e.target as Node)) {
				setContextMenu(null)
			}
		}
		if (contextMenu) {
			document.addEventListener("mousedown", handleClickOutside)
		}

		return () => {
			document.removeEventListener("mousedown", handleClickOutside)
		}
	}, [contextMenu])

	const handleContextMenu = (e: React.MouseEvent, paperId: string) => {
		e.preventDefault()
		setContextMenu({ x: e.clientX, y: e.clientY, paperId })
	}

	const handleDelete = () => {
		if (contextMenu) {
			onDeletePaper?.(contextMenu.paperId)
			setContextMenu(null)
		}
	}

	return (
		<div className="w-56 h-full bg-[#1a1a1a] border-r border-white/10 flex flex-col">
			<div className="p-4 border-b border-white/10">
				<h1 className="text-sm font-semibold text-white/90">Research Agent</h1>
				<p className="text-xs text-white/50 mt-0.5">
					{papers.length} paper{papers.length !== 1 ? "s" : ""}
				</p>
			</div>
			<div className="flex-1 overflow-y-auto py-2">
				{papers.length === 0 ? (
					<p className="px-4 py-2 text-xs text-white/40">No papers yet</p>
				) : (
					papers.map(paper => {
						const isDeleting = deletingPaperId === paper.id
						return (
							<div
								key={paper.id}
								onClick={() => !isDeleting && onPaperClick?.(paper)}
								onContextMenu={e => !isDeleting && handleContextMenu(e, paper.id)}
								className={`px-4 py-2 text-xs transition-colors ${
									isDeleting ? "opacity-50 cursor-not-allowed" : "cursor-pointer hover:bg-white/5"
								} ${
									selectedPaperId === paper.id
										? "bg-[#4A9D9A]/20 text-white border-l-2 border-[#4A9D9A]"
										: "text-white/70"
								}`}
							>
								<div className="flex items-center gap-2">
									{isDeleting && <Loader2 className="w-3 h-3 animate-spin text-white/50" />}
									<p className="truncate flex-1">{paper.title}</p>
								</div>
							</div>
						)
					})
				)}
			</div>

			{/* Context Menu */}
			{contextMenu && (
				<div
					ref={contextMenuRef}
					className="fixed bg-[#2a2a2a] border border-white/10 rounded shadow-lg py-1 z-50"
					style={{ left: contextMenu.x, top: contextMenu.y }}
				>
					<button
						onClick={handleDelete}
						className="flex items-center gap-2 px-3 py-1.5 text-xs text-red-400 hover:bg-white/10 w-full text-left"
					>
						<Trash2 className="w-3 h-3" />
						Delete
					</button>
				</div>
			)}
		</div>
	)
}

export default Sidebar
