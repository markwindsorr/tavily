"use client"

import { motion, AnimatePresence } from "framer-motion"
import { ArrowRight } from "lucide-react"
import { ArxivCategory } from "@/lib/constants"
import { PROMPTS_BY_CATEGORY } from "@/lib/prompts"

interface PromptGridProps {
	selectedCategory: ArxivCategory
	onPromptSelect: (prompt: string) => void
}

const PromptGrid = ({ selectedCategory, onPromptSelect }: PromptGridProps) => {
	const prompts = PROMPTS_BY_CATEGORY[selectedCategory]

	return (
		<AnimatePresence mode="wait">
			<motion.div
				key={selectedCategory || "default"}
				initial={{ opacity: 0, y: 10 }}
				animate={{ opacity: 1, y: 0 }}
				exit={{ opacity: 0, y: -10 }}
				transition={{ duration: 0.2 }}
				className="space-y-2"
			>
				{prompts.map(prompt => (
					<button
						key={prompt.id}
						onClick={() => onPromptSelect(prompt.text)}
						className="w-full flex items-center justify-between px-4 py-3 rounded-lg
              bg-white/5 border border-white/10 text-left
              hover:bg-white/10 hover:border-white/20 transition-all duration-200
              group"
					>
						<span className="text-sm text-white/80 group-hover:text-white">{prompt.text}</span>
						<ArrowRight className="w-4 h-4 text-white/40 group-hover:text-[#4A9D9A] transition-colors" />
					</button>
				))}
			</motion.div>
		</AnimatePresence>
	)
}

export default PromptGrid
