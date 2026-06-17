import type { AnalystMessage } from "../data/dashboardTypes";

type ChatPlaceholderProps = {
	analyst: AnalystMessage[];
};

export function ChatPlaceholder({ analyst }: ChatPlaceholderProps) {
	return (
		<section
			className="panel chat-panel"
			id="analyst"
			aria-labelledby="analyst-heading"
		>
			<p className="eyebrow">AI workspace</p>
			<h2 id="analyst-heading">AI analyst chat</h2>
			<div className="chat-panel__messages">
				{analyst.map((message) => (
					<div
						className={`chat-message chat-message--${message.role}`}
						key={message.text}
					>
						<span>{message.role === "assistant" ? "Analyst" : "You"}</span>
						<p>{message.text}</p>
					</div>
				))}
			</div>
			<button className="button button--secondary" type="button">
				Ask analyst
			</button>
		</section>
	);
}
