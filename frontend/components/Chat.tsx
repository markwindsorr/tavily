"use client"

import { useState, useRef, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { sendChatMessage, selectPaper, getChatHistory, clearChatHistory, ChatResponse, PaperCandidate } from "@/lib/api"
import { Loader2 } from "lucide-react"
import { CHAT_STORAGE_KEY } from "@/lib/constants"
import { ArxivCategory } from "@/lib/constants"
import GreetingSection from "./GreetingSection"
import CategoryChips from "./CategoryChips"
import PromptGrid from "./PromptGrid"
import TextInput from "./TextInput"

interface Message {
	role: "user" | "assistant"
	content: string
	paper_candidates?: PaperCandidate[]
}

interface ChatProps {
	onGraphUpdate?: () => void
}

const Chat = ({ onGraphUpdate }: ChatProps) => {
	const [messages, setMessages] = useState<Message[]>([])
	const [input, setInput] = useState("")
	const [loading, setLoading] = useState(false)
	const [clearing, setClearing] = useState(false)
	const [selectedCategory, setSelectedCategory] = useState<ArxivCategory | null>(null)
	const [isHydrated, setIsHydrated] = useState(false)
	const messagesEndRef = useRef<HTMLDivElement>(null)
	const messagesContainerRef = useRef<HTMLDivElement>(null)
	const prevMessageCount = useRef(0)

	const isInitialState = messages.length === 0 && isHydrated

	useEffect(() => {
		const saved = localStorage.getItem(CHAT_STORAGE_KEY)
		if (saved) {
			try {
				const parsed = JSON.parse(saved)
				if (parsed.length > 0) {
					setMessages(parsed)
					setIsHydrated(true)
					return // Use localStorage, don't overwrite with backend since it makes chat message paper list dissapear from ChatMessage
				}
			} catch {}
		}
		setIsHydrated(true)

		const loadHistory = async () => {
			try {
				const history = await getChatHistory()
				if (history.length > 0) {
					const loadedMessages: Message[] = history.map(msg => ({
						role: msg.role as "user" | "assistant",
						content: msg.content
					}))
					setMessages(loadedMessages)
				}
			} catch (error) {
				console.error("Failed to load chat history:", error)
			}
		}
		loadHistory()
	}, [])

	useEffect(() => {
		if (isHydrated && messages.length > 0) {
			localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages))
		}
	}, [messages, isHydrated])

	const handleClearChat = async () => {
		setClearing(true)
		try {
			await clearChatHistory()
			setMessages([])
			localStorage.removeItem(CHAT_STORAGE_KEY)
		} catch (error) {
			console.error("Failed to clear chat history:", error)
		} finally {
			setClearing(false)
		}
	}

	const scrollToBottom = (smooth = true) => {
		if (messagesContainerRef.current) {
			const container = messagesContainerRef.current
			container.scrollTo({
				top: container.scrollHeight,
				behavior: smooth ? "smooth" : "auto"
			})
		}
	}

	useEffect(() => {
		requestAnimationFrame(() => {
			const isFirstMessage = prevMessageCount.current === 0 && messages.length > 0
			scrollToBottom(!isFirstMessage)
			prevMessageCount.current = messages.length
		})
	}, [messages])

	const handleSend = async (messageText?: string) => {
		const text = messageText || input
		if (!text.trim() || loading) return
		const userMessage = text.trim()
		setInput("")
		setMessages(prev => [...prev, { role: "user", content: userMessage }])
		setLoading(true)
		try {
			const response: ChatResponse = await sendChatMessage(userMessage)
			setMessages(prev => [
				...prev,
				{
					role: "assistant",
					content: response.message,
					paper_candidates: response.paper_candidates
				}
			])
			if (response.graph_updated && onGraphUpdate) {
				onGraphUpdate()
			}
		} catch (error) {
			setMessages(prev => [
				...prev,
				{
					role: "assistant",
					content: "Sorry, there was an error processing your request."
				}
			])
		} finally {
			setLoading(false)
		}
	}

	const handlePromptSelect = (prompt: string) => {
		setInput(prompt)
		handleSend(prompt)
	}

	const handleSelectPaper = async (arxivId: string, sourcePaperId?: string) => {
		setLoading(true)
		try {
			const response = await selectPaper(arxivId, sourcePaperId)
			setMessages(prev => [...prev, { role: "assistant", content: response.message }])
			if (response.graph_updated && onGraphUpdate) {
				onGraphUpdate()
			}
		} catch (error) {
			setMessages(prev => [...prev, { role: "assistant", content: "Error adding paper. Please try again." }])
		} finally {
			setLoading(false)
		}
	}

	return (
		<div className="flex flex-col h-full bg-[#1e1e1e]">
			<AnimatePresence mode="wait">
				{isInitialState ? (
					<motion.div
						key="initial"
						initial={{ opacity: 0 }}
						animate={{ opacity: 1 }}
						exit={{ opacity: 0, y: -20 }}
						transition={{ duration: 0.3 }}
						className="flex-1 flex items-start justify-center overflow-y-auto pt-[15vh]"
					>
						<div className="w-full max-w-xl px-6">
							<GreetingSection />
							<div className="mb-6">
								<TextInput
									value={input}
									onChange={setInput}
									onSubmit={() => handleSend()}
									disabled={loading}
								/>
							</div>
							<CategoryChips selectedCategory={selectedCategory} onCategorySelect={setSelectedCategory} />
							{selectedCategory && (
								<PromptGrid selectedCategory={selectedCategory} onPromptSelect={handlePromptSelect} />
							)}
						</div>
					</motion.div>
				) : (
					<motion.div
						key="active"
						initial={{ opacity: 0 }}
						animate={{ opacity: 1 }}
						transition={{ duration: 0.3 }}
						className="flex flex-col h-full"
					>
						<div ref={messagesContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4">
							{messages.map((msg, idx) => (
								<motion.div
									key={idx}
									initial={{ opacity: 0, y: 10 }}
									animate={{ opacity: 1, y: 0 }}
									transition={{ duration: 0.2 }}
									className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
								>
									<div
										className={`max-w-[80%] rounded-lg px-4 py-2 ${
											msg.role === "user"
												? "bg-[#4A9D9A] text-white"
												: "bg-[#2a2a2a] text-white/90"
										}`}
									>
										<p className="whitespace-pre-wrap text-sm">{msg.content}</p>
										{msg.paper_candidates && msg.paper_candidates.length > 0 && (
											<div className="mt-3 space-y-2">
												{msg.paper_candidates.map((paper, paperIdx) => (
													<button
														key={`${idx}-${paperIdx}-${paper.arxiv_id}`}
														onClick={() =>
															handleSelectPaper(paper.arxiv_id, paper.source_paper_id)
														}
														disabled={loading}
														className="block w-full text-left p-2 bg-white/10 rounded hover:bg-white/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
													>
														<div className="font-medium text-sm truncate">
															{paper.title}
														</div>
														<div className="text-xs text-white/60">
															{paper.authors.slice(0, 2).join(", ")}
															{paper.authors.length > 2 ? " et al." : ""} · {paper.year} ·{" "}
															{paper.arxiv_id}
														</div>
													</button>
												))}
											</div>
										)}
									</div>
								</motion.div>
							))}

							{loading && (
								<div className="flex justify-start">
									<div className="bg-[#2a2a2a] rounded-lg px-4 py-3">
										<div className="flex space-x-1.5">
											<div
												className="w-2 h-2 bg-white/50 rounded-full animate-bounce"
												style={{ animationDelay: "0ms" }}
											/>
											<div
												className="w-2 h-2 bg-white/50 rounded-full animate-bounce"
												style={{ animationDelay: "150ms" }}
											/>
											<div
												className="w-2 h-2 bg-white/50 rounded-full animate-bounce"
												style={{ animationDelay: "300ms" }}
											/>
										</div>
									</div>
								</div>
							)}

							<div ref={messagesEndRef} />
						</div>
						<div className="p-4 border-t border-white/10">
							<div className="flex items-center gap-2">
								<div className="flex-1">
									<TextInput
										value={input}
										onChange={setInput}
										onSubmit={() => handleSend()}
										disabled={loading}
									/>
								</div>
								<button
									onClick={handleClearChat}
									disabled={loading || clearing}
									className="px-3 py-2 text-sm text-white/60 hover:text-white/90 hover:bg-white/10 rounded transition-colors disabled:opacity-50 flex items-center gap-1.5"
									title="Clear chat"
								>
									{clearing ? (
										<>
											<Loader2 className="w-3.5 h-3.5 animate-spin" />
											Clearing...
										</>
									) : (
										"Clear"
									)}
								</button>
							</div>
						</div>
					</motion.div>
				)}
			</AnimatePresence>
		</div>
	)
}

export default Chat
