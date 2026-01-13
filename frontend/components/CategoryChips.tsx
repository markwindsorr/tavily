"use client"

import { CATEGORIES, ArxivCategory } from "@/lib/constants"

interface CategoryChipsProps {
	selectedCategory: ArxivCategory | null
	onCategorySelect: (category: ArxivCategory | null) => void
}

const CategoryChips = ({ selectedCategory, onCategorySelect }: CategoryChipsProps) => {
	const handleClick = (categoryId: ArxivCategory) => {
		if (selectedCategory === categoryId) {
			onCategorySelect(null)
		} else {
			onCategorySelect(categoryId)
		}
	}

	return (
		<div className="flex gap-1.5 justify-center mb-6">
			{CATEGORIES.map(category => {
				const isSelected = selectedCategory === category.id

				return (
					<button
						key={category.id}
						onClick={() => handleClick(category.id)}
						className={`px-2 py-0.5 rounded border text-[11px] font-mono transition-all duration-200 active:scale-95 ${
							isSelected
								? "bg-[#4A9D9A]/20 border-[#4A9D9A] text-white"
								: "bg-white/5 border-white/10 text-white/60 hover:bg-white/10 hover:text-white/90"
						}`}
					>
						{category.label}
					</button>
				)
			})}
		</div>
	)
}

export default CategoryChips
