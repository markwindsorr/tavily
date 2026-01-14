"use client"

import { useState, useEffect } from "react"
import { Paper } from "@/lib/api"
import { X, MessageSquare } from "lucide-react"
import Chat from "./Chat"
import PaperTab from "./PaperTab"

interface Tab {
	id: string
	type: "chat" | "paper"
	title: string
	paper?: Paper
}

interface TabbedPaneProps {
	onGraphUpdate?: () => void
	openPapers: Paper[]
	onClosePaper: (paperId: string) => void
	selectedTabId?: string
	onSelectTab: (tabId: string) => void
}

const TabbedPane = ({ onGraphUpdate, openPapers, onClosePaper, selectedTabId, onSelectTab }: TabbedPaneProps) => {
	const [activeTabId, setActiveTabId] = useState<string>("chat")

	const tabs: Tab[] = [
		{ id: "chat", type: "chat", title: "Chat" },
		...openPapers.map(paper => ({
			id: paper.id,
			type: "paper" as const,
			title: paper.title.length > 20 ? paper.title.slice(0, 20) + "..." : paper.title,
			paper
		}))
	]

	useEffect(() => {
		if (selectedTabId && selectedTabId !== activeTabId) {
			const tab = tabs.find(t => t.id === selectedTabId)
			if (tab) {
				setActiveTabId(selectedTabId)
			}
		}
	}, [selectedTabId, tabs, activeTabId])

	const handleTabClick = (tabId: string) => {
		setActiveTabId(tabId)
		onSelectTab(tabId)
	}

	const handleCloseTab = (e: React.MouseEvent, tab: Tab) => {
		e.stopPropagation()
		if (tab.type === "paper") {
			onClosePaper(tab.id)
		}
		if (activeTabId === tab.id) {
			setActiveTabId("chat")
		}
	}

	const activeTab = tabs.find(t => t.id === activeTabId) || tabs[0]

	return (
		<div className="flex flex-col h-full">
			<div className="flex-shrink-0 flex items-end bg-[#1a1a1a] border-b border-white/10 overflow-x-auto" style={{ height: 40 }}>
				{tabs.map(tab => (
					<div
						key={tab.id}
						onClick={() => handleTabClick(tab.id)}
						className={`flex items-center gap-2 px-4 h-full text-xs font-medium border-r border-white/5 transition-colors min-w-0 cursor-pointer ${
							activeTabId === tab.id
								? "bg-[#1e1e1e] text-white border-b-2 border-b-[#4A9D9A]"
								: "text-white/50 hover:text-white/80 hover:bg-white/5"
						}`}
					>
						{tab.type === "chat" ? <MessageSquare className="w-3.5 h-3.5 flex-shrink-0" /> : null}
						<span className="truncate max-w-[120px]">{tab.title}</span>
						{tab.type !== "chat" && (
							<button
								onClick={e => handleCloseTab(e, tab)}
								className="ml-1 p-0.5 rounded hover:bg-white/10 flex-shrink-0"
							>
								<X className="w-3 h-3" />
							</button>
						)}
					</div>
				))}
			</div>
			<div className="flex-1 overflow-hidden">
				{activeTab.type === "chat" ? (
					<Chat onGraphUpdate={onGraphUpdate} />
				) : activeTab.type === "paper" && activeTab.paper ? (
					<PaperTab paper={activeTab.paper} onGraphUpdate={onGraphUpdate} />
				) : null}
			</div>
		</div>
	)
}

export default TabbedPane
