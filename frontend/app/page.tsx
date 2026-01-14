"use client"

import { useState, useEffect, useCallback } from "react"
import Sidebar from "@/components/Sidebar"
import GraphView from "@/components/GraphView"
import TabbedPane from "@/components/TabbedPane"
import { getPapers, getCytoscapeGraph, deletePaper, deleteEdge, Paper, CytoscapeGraph } from "@/lib/api"

const Home = () => {
	const [papers, setPapers] = useState<Paper[]>([])
	const [graphData, setGraphData] = useState<CytoscapeGraph | null>(null)
	const [openPapers, setOpenPapers] = useState<Paper[]>([])
	const [selectedTabId, setSelectedTabId] = useState<string | undefined>()
	const [deletingPaperId, setDeletingPaperId] = useState<string | null>(null)

	const fetchData = useCallback(async () => {
		try {
			const [papersData, graphDataResult] = await Promise.all([getPapers(), getCytoscapeGraph()])
			setPapers(papersData)
			setGraphData(graphDataResult)
		} catch (error) {
			console.error("Error fetching data:", error)
		}
	}, [])

	useEffect(() => {
		fetchData()
	}, [fetchData])

	const handleGraphUpdate = () => {
		fetchData()
	}

	const openPaperTab = (paper: Paper) => {
		if (!openPapers.find(p => p.id === paper.id)) {
			setOpenPapers(prev => [...prev, paper])
		}
		setSelectedTabId(paper.id)
	}

	const handlePaperClick = (paper: Paper) => {
		openPaperTab(paper)
	}

	const handleNodeClick = (nodeId: string) => {
		const paper = papers.find(p => p.id === nodeId)
		if (paper) {
			openPaperTab(paper)
		}
	}

	const handleClosePaper = (paperId: string) => {
		setOpenPapers(prev => prev.filter(p => p.id !== paperId))
		if (selectedTabId === paperId) {
			setSelectedTabId(undefined)
		}
	}

	const handleSelectTab = (tabId: string) => {
		setSelectedTabId(tabId === "chat" ? undefined : tabId)
	}

	const handleDeletePaper = async (paperId: string) => {
		setDeletingPaperId(paperId)
		try {
			await deletePaper(paperId)
			handleClosePaper(paperId)
			await fetchData()
		} catch (error) {
			console.error("Error deleting paper:", error)
		} finally {
			setDeletingPaperId(null)
		}
	}

	const handleDeleteEdge = async (edgeId: string) => {
		try {
			await deleteEdge(edgeId)
			await fetchData()
		} catch (error) {
			console.error("Error deleting edge:", error)
		}
	}

	return (
		<div className="flex h-screen bg-[#1a1a1a]">
			<Sidebar
				papers={papers}
				onPaperClick={handlePaperClick}
				onDeletePaper={handleDeletePaper}
				selectedPaperId={selectedTabId}
				deletingPaperId={deletingPaperId}
			/>
			<div className="flex-1 flex">
				<div className="w-1/2 border-r border-white/10">
					<TabbedPane
						onGraphUpdate={handleGraphUpdate}
						openPapers={openPapers}
						onClosePaper={handleClosePaper}
						selectedTabId={selectedTabId}
						onSelectTab={handleSelectTab}
					/>
				</div>
				<div className="w-1/2 flex flex-col">
					<div className="flex-shrink-0 border-b border-white/10 bg-[#1e1e1e] flex items-center justify-between px-4" style={{ height: 40 }}>
						<span className="text-xs font-medium text-white/70">Connection Graph</span>
						<div className="text-xs text-white/40">
							{graphData?.elements.filter(e => !e.data.source).length || 0} nodes &middot;{" "}
							{graphData?.elements.filter(e => e.data.source).length || 0} edges
						</div>
					</div>
					<div className="flex-1 bg-[#1e1e1e]">
						<GraphView
							graphData={graphData}
							onNodeClick={handleNodeClick}
							onEdgeDelete={handleDeleteEdge}
						/>
					</div>
				</div>
			</div>
		</div>
	)
}

export default Home
