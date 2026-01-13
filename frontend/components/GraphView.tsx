"use client"

import { useEffect, useRef, useState } from "react"
import { CytoscapeGraph } from "@/lib/api"
import { Plus, Minus, Maximize2, Trash2 } from "lucide-react"
import type { Core } from "cytoscape"

interface GraphViewProps {
	graphData: CytoscapeGraph | null
	onNodeClick?: (nodeId: string) => void
	onEdgeDelete?: (edgeId: string) => void
}

const LAYOUT_CONFIG = {
	name: "cose" as const,
	animate: true,
	animationDuration: 500,
	nodeRepulsion: () => 8000,
	idealEdgeLength: () => 100,
	gravity: 0.25
}

const GraphView = ({ graphData, onNodeClick, onEdgeDelete }: GraphViewProps) => {
	const containerRef = useRef<HTMLDivElement>(null)
	const cyRef = useRef<Core | null>(null)
	const [selectedEdge, setSelectedEdge] = useState<Record<string, unknown> | null>(null)
	const [isInitialized, setIsInitialized] = useState(false)
	const onNodeClickRef = useRef(onNodeClick)

	useEffect(() => {
		onNodeClickRef.current = onNodeClick
	}, [onNodeClick])

	useEffect(() => {
		let mounted = true
		const initCytoscape = async () => {
			if (!containerRef.current) return
			const cytoscape = (await import("cytoscape")).default
			if (!mounted) return
			cyRef.current = cytoscape({
				container: containerRef.current,
				elements: graphData?.elements || [],
				minZoom: 0.2,
				maxZoom: 3,
				boxSelectionEnabled: false,
				autounselectify: false,
				style: [
					{
						selector: "node",
						style: {
							"background-color": "#4A9D9A",
							label: "data(label)",
							color: "#fff",
							"text-valign": "center",
							"text-halign": "center",
							"font-size": "10px",
							"text-wrap": "wrap",
							"text-max-width": "80px",
							width: "50px",
							height: "50px",
							"border-width": "2px",
							"border-color": "#3d857f"
						}
					},
					{
						selector: "edge",
						style: {
							width: 2,
							"line-color": "#555",
							"target-arrow-color": "#555",
							"target-arrow-shape": "triangle",
							"curve-style": "bezier",
							label: "data(label)",
							"font-size": "8px",
							color: "#888",
							"text-rotation": "autorotate",
							events: "yes"
						}
					},
					{
						selector: "edge[edge_type='citation']",
						style: {
							"line-color": "#4A9D9A",
							"target-arrow-color": "#4A9D9A"
						}
					},
					{
						selector: "edge[edge_type='semantic']",
						style: {
							"line-color": "#8B5CF6",
							"target-arrow-color": "#8B5CF6",
							"line-style": "dashed"
						}
					},
					{
						selector: ":selected",
						style: {
							"background-color": "#F59E0B",
							"border-color": "#D97706"
						}
					}
				],
				layout: LAYOUT_CONFIG
			})

			cyRef.current.on("tap", "node", evt => {
				const nodeId = evt.target.id()
				onNodeClickRef.current?.(nodeId)
			})

			cyRef.current.on("tap", "edge", evt => {
				evt.stopPropagation()
				setSelectedEdge(evt.target.data())
			})

			setIsInitialized(true)
		}

		initCytoscape()

		return () => {
			mounted = false
			if (cyRef.current) {
				cyRef.current.destroy()
			}
		}
	}, [])

	useEffect(() => {
		if (cyRef.current && graphData && isInitialized) {
			cyRef.current.elements().remove()
			cyRef.current.add(graphData.elements)
			const layout = cyRef.current.layout(LAYOUT_CONFIG)
			layout.on("layoutstop", () => {
				if (cyRef.current) {
					cyRef.current.fit(undefined, 50)
					// Limit zoom for small graphs
					if (cyRef.current.zoom() > 1.5) {
						cyRef.current.zoom(1.5)
						cyRef.current.center()
					}
				}
			})
			layout.run()
		}
	}, [graphData, isInitialized])

	const handleFitView = () => {
		if (cyRef.current) {
			cyRef.current.fit(undefined, 50)
			if (cyRef.current.zoom() > 1.5) {
				cyRef.current.zoom(1.5)
				cyRef.current.center()
			}
		}
	}

	const handleZoomIn = () => {
		const currentZoom = cyRef.current?.zoom() || 1
		cyRef.current?.zoom(currentZoom * 1.2)
	}

	const handleZoomOut = () => {
		const currentZoom = cyRef.current?.zoom() || 1
		cyRef.current?.zoom(currentZoom * 0.8)
	}

	return (
		<div className="relative h-full w-full">
			<div ref={containerRef} className="h-full w-full bg-[#1e1e1e]" />
			<div className="absolute top-4 right-4 flex flex-col gap-1">
				<button
					onClick={handleZoomIn}
					className="p-2 bg-[#2a2a2a] rounded border border-white/10 hover:bg-[#333] text-white/70 hover:text-white transition-colors"
					title="Zoom in"
				>
					<Plus className="w-4 h-4" />
				</button>
				<button
					onClick={handleZoomOut}
					className="p-2 bg-[#2a2a2a] rounded border border-white/10 hover:bg-[#333] text-white/70 hover:text-white transition-colors"
					title="Zoom out"
				>
					<Minus className="w-4 h-4" />
				</button>
				<button
					onClick={handleFitView}
					className="p-2 bg-[#2a2a2a] rounded border border-white/10 hover:bg-[#333] text-white/70 hover:text-white transition-colors"
					title="Fit view"
				>
					<Maximize2 className="w-4 h-4" />
				</button>
			</div>
			<div className="absolute bottom-4 left-4 bg-[#2a2a2a] border border-white/10 p-3 rounded text-xs">
				<p className="font-medium mb-2 text-white/70">Legend</p>
				<div className="flex items-center gap-2 mb-1 text-white/60">
					<div className="w-4 h-0.5 bg-[#4A9D9A]" />
					<span>Citation</span>
				</div>
				<div className="flex items-center gap-2 text-white/60">
					<div className="w-4 h-0.5 bg-purple-500 border-dashed" />
					<span>Semantic</span>
				</div>
			</div>
			{selectedEdge && (
				<div className="absolute bottom-4 right-4 bg-[#2a2a2a] border border-white/10 p-3 rounded max-w-xs">
					<div className="flex justify-between items-start">
						<p className="font-medium text-sm text-white/90">Connection Details</p>
						<button onClick={() => setSelectedEdge(null)} className="text-white/40 hover:text-white/60">
							&times;
						</button>
					</div>
					<p className="text-xs text-white/50 mt-1">Type: {String(selectedEdge.edge_type)}</p>
					{selectedEdge.evidence ? (
						<p className="text-xs text-white/70 mt-2">{String(selectedEdge.evidence)}</p>
					) : null}
					{onEdgeDelete && selectedEdge.id ? (
						<button
							onClick={() => {
								onEdgeDelete(String(selectedEdge.id))
								setSelectedEdge(null)
							}}
							className="mt-3 flex items-center gap-1.5 text-xs text-red-400 hover:text-red-300"
						>
							<Trash2 className="w-3 h-3" />
							Delete connection
						</button>
					) : null}
				</div>
			)}

			{/* Empty state */}
			{(!graphData || graphData.elements.length === 0) && (
				<div className="absolute inset-0 flex items-center justify-center pointer-events-none">
					<div className="text-center text-white/40">
						<p className="text-sm">No papers in graph yet.</p>
						<p className="text-xs mt-1">Add papers via the chat to build your graph.</p>
					</div>
				</div>
			)}
		</div>
	)
}

export default GraphView
