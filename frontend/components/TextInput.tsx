"use client"

import { useRef, useEffect, KeyboardEvent } from "react"
import { ArrowUp } from "lucide-react"

interface TextInputProps {
	value: string
	onChange: (value: string) => void
	onSubmit: () => void
	placeholder?: string
	disabled?: boolean
}

const TextInput = ({
	value,
	onChange,
	onSubmit,
	placeholder = "Add a paper, ask a question, or find connections...",
	disabled = false
}: TextInputProps) => {
	const textareaRef = useRef<HTMLTextAreaElement>(null)

	useEffect(() => {
		if (textareaRef.current) {
			textareaRef.current.style.height = "auto"
			const newHeight = Math.min(textareaRef.current.scrollHeight, 200)
			textareaRef.current.style.height = newHeight + "px"
		}
	}, [value])

	const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault()
			if (value.trim() && !disabled) {
				onSubmit()
			}
		}
	}

	const canSend = value.trim().length > 0 && !disabled

	return (
		<div className="w-full">
			<div
				className="flex flex-col bg-[#222222] rounded-lg border border-white/10
					shadow-lg hover:border-white/20
					focus-within:border-[#4A9D9A]/50 transition-all duration-200"
			>
				<div className="p-3 flex flex-col gap-2">
					<div className="relative min-h-[2.5rem] max-h-48 w-full overflow-y-auto">
						<textarea
							ref={textareaRef}
							value={value}
							onChange={e => onChange(e.target.value)}
							onKeyDown={handleKeyDown}
							disabled={disabled}
							placeholder={placeholder}
							className="w-full resize-none bg-transparent text-sm text-white/90
								placeholder:text-white/40 outline-none
								disabled:opacity-50 disabled:cursor-not-allowed"
							style={{ minHeight: "2.5rem" }}
						/>
					</div>

					<div className="flex items-center justify-end">
						<button
							onClick={onSubmit}
							disabled={!canSend}
							className={`flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-200
								${
									canSend
										? "bg-[#4A9D9A] hover:bg-[#3d857f] text-white active:scale-95"
										: "bg-white/10 text-white/30 cursor-not-allowed"
								}`}
						>
							<ArrowUp className="w-4 h-4" />
						</button>
					</div>
				</div>
			</div>
		</div>
	)
}

export default TextInput
