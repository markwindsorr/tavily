import Image from "next/image"

const GreetingSection = () => {
	return (
		<div className="flex justify-center mb-8">
			<Image src="/tavilyLogo.svg" alt="Tavily" width={132} height={132} className="brightness-0 invert" />
		</div>
	)
}

export default GreetingSection
